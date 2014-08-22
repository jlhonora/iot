#!/usr/bin/env python
import time
import psycopg2
import sensor
import camera_manager

# Laps threshold
threshold = 9

def get_last_sample():
    with psycopg2.connect("dbname=pgtest2db user=pgtest2user") as dbconn:
        with dbconn.cursor() as cursor:
            counter = sensor.Sensor.get_by_name(cursor, "Antu Counter")
            cursor.execute("SELECT value, created_at FROM measurements WHERE (sensor_id = (%s)) ORDER BY id DESC LIMIT 1", (counter.id,))
            meas = cursor.fetchall()
            return meas[0]

def is_active(last_sample, current_sample):
    if last_sample is None:
        return False
    laps = current_sample[0]
    timestamp = current_sample[1]
    if last_sample[1] == timestamp:
        return False
    
    return (laps - last_sample[0]) > threshold

def discard_video(filename):
    print "Discarding " + str(filename)

def save_video(filename):
    print "Saving " + str(filename)

if __name__ == '__main__':
    camera = camera_manager.CameraManager()
    last_sample = None
    current_sample = None
    while True:
        # Check if we should be filming
        current_sample = get_last_sample()
        video = None
        if is_active(last_sample, current_sample):
            print "Is active, filming"
            camera.capture_video_async()
            time.sleep(12)
            video = camera.last_video
        else:
            print "Not active"

        # Update sample
        last_sample = current_sample
        current_sample = get_last_sample()

        # If still active, save
        if is_active(last_sample, current_sample) and video is not None:
            save_video(video)
        else:
            discard_video(video)

        # Sleep some time
        time.sleep(1)
