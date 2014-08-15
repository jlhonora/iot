#!/usr/bin/env python
# Utils for the Pi NoIR and Pi Camera
import picamera
import time
import os
import threading

class CameraManager:
    camera = None
    last_video = None
    last_image = None

    def __init__(self):
        self.camera = picamera.PiCamera()

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

        # Replace old reference with new one
        if replace_old and self.last_video is not None:
            old_file = self.last_video
            self.last_video = current_file
            os.remove(old_file)
        else:
            self.last_video = current_file
            
        return current_file

    def capture_image(self, replace_old = True):
        current_file = self.get_image_filename()
        self.camera.capture(current_file)

        # Replace old reference with new one
        if replace_old and self.last_image is not None:
            old_file = self.last_image
            self.last_image = current_file
            os.remove(old_file)
        else:
            self.last_image = current_file
        return current_file

if __name__ == '__main__':
    manager = CameraManager()
    manager.capture_image()
    print "Captured image %s" % manager.last_image
    manager.capture_video_async()
    time.sleep(13)
    print "Captured video %s" % manager.last_video
