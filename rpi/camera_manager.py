#!/usr/bin/env python
# Utils for the Pi NoIR and Pi Camera
import picamera
import time
import os
import threading
import traceback
import RPi.GPIO as GPIO

class CameraManager:
    camera = None
    last_video = None
    last_image = None
    light_channel = 16 # Connected to board pin 16 (BCM GPIO 23)

    def setup(self):
        self.camera = picamera.PiCamera()
        self.camera.exposure_mode = "night"
        self.camera.brightness = 55
        self.init_light()

    def init_light(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.light_channel, GPIO.OUT, initial = GPIO.LOW)

    def light(self, turn_on = True):
        if self.light_channel is None:
            return
        GPIO.output(self.light_channel, turn_on) 

    def get_video_filename(self):
        return 'assets/' + str(int(time.time())) + '.h264'

    def get_image_filename(self):
        return 'assets/' + str(int(time.time())) + '.jpg'

    def capture_video_async(self, seconds = 12, replace_old = True):
        t = threading.Thread(target = self.capture_video, args = (seconds, replace_old))
        t.start()

    def capture_video(self, seconds = 12, replace_old = True):
        current_file = self.get_video_filename()
        self.camera.start_recording(current_file)
        time.sleep(seconds)
        self.camera.stop_recording()
        os.chmod(current_file, 0666)

        # Replace old reference with new one
        if replace_old:
            old_file = self.last_video
            self.last_video = current_file
            if old_file is not None:
                try:
                    os.remove(old_file)
                except OSError, e:
                    print traceback.format_exc(e)
                    pass
        else:
            self.last_video = current_file
            
        return current_file

    def capture_image(self, replace_old = True):
        current_file = self.get_image_filename()
        self.camera.capture(current_file)
        os.chmod(current_file, 0666)

        # Replace old reference with new one
        if replace_old:
            old_file = self.last_image
            self.last_image = current_file
            if old_file is not None:
                os.remove(old_file)
        else:
            self.last_image = current_file
        return current_file

    def cleanup(self):
        self.light(False)
        GPIO.cleanup(self.light_channel)
        self.camera.close()
        self.camera = None

if __name__ == '__main__':
    GPIO.cleanup()
    manager = CameraManager()
    manager.setup()
    #manager.capture_image()
    print "Captured image %s" % manager.last_image
    manager.light(True)
    manager.capture_video_async()
    time.sleep(12)
    manager.light(False)
    print "Captured video %s" % manager.last_video
    manager.cleanup()
