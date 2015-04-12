#!/usr/bin/env python
import camera_manager
import datetime
from dateutil import parser
import os
import psycopg2
import sensor
import time
import traceback
import youtube_manager
import yaml

# Laps threshold
threshold = 2

def get_last_sample():
    with psycopg2.connect("dbname=pgtest2db user=pgtest2user") as dbconn:
        with dbconn.cursor() as cursor:
            counter = sensor.Sensor.get_by_name(cursor, "Antu Counter")
            cursor.execute("SELECT value, created_at FROM measurements WHERE (sensor_id = (%s)) ORDER BY id DESC LIMIT 1", (counter.id,))
            meas = cursor.fetchall()
            return meas[0]

def is_active(old_sample, new_sample):
    if old_sample is None:
        return False
    laps = new_sample[0]
    timestamp = new_sample[1]
    
    if (int(new_sample[0]) - int(old_sample[0])) >= threshold:
        return True
    return False

def discard_video(filename):
    if filename is None:
        return
    print "Discarding " + str(filename)
    try:
        os.remove(filename)
    except OSError, e:
        print traceback.format_exc(e)
        pass

def video_available(filename = 'video.yml'):
    if not os.path.exists(filename): 
        return False
    video_date = None
    video_url = None
    video_is_uploaded = False
    with open(filename, 'r') as f:
        doc = yaml.load(f)
        if 'date' in doc:
          video_date = parser.parse(doc['date'])
        if 'url' in doc:
          video_url = doc['url']
        if 'uploaded' in doc:
          video_is_uploaded = doc['uploaded'] != "False"

    # We can't use an already uploaded video
    if video_is_uploaded:
        return True

    # Check for a valid URL
    if video_url is None or len(video_url) == 0:
        return False

    # Videos newer than 12 hours ago are valid
    twelve_hours_ago = datetime.datetime.now() - datetime.datetime.timedelta(hours = 12)
    if video_date is not None and (video_date > twelve_hours_ago):
        return True

def write_video_state(data, filename = 'video.yml'):
    with os.fdopen(os.open(filename, os.O_WRONLY | os.O_CREAT), 'w') as outfile:
        outfile.truncate()
        outfile.write(yaml.dump(data, default_flow_style=False))
    os.chmod(filename, 0666)

def attempt_upload(filename):
    data = dict(
        date = str(datetime.datetime.now()),
        uploaded = "Uploading")
    write_video_state(data)
    result = youtube_manager.upload_video(filename)
    if result is None or len(result) == 0:
        data['uploaded'] = str(False)
        write_video_state(data)
        return False
    data['uploaded'] = str(True)
    data['url'] = result
    write_video_state(data)

def save_video(filename, force_upload = True):
    if filename is None:
        print "Invalid filename"
        return
    if not force_upload and video_available():
        print "Video available, discarding"
        discard_video(filename)
        return
    print "Saving " + str(filename)
    attempt_upload(filename)

def should_be_sleeping():
    now = datetime.datetime.utcnow()
    finish = now.replace(hour = 10, minute = 0, second = 0)
    start = now.replace(hour = 23, minute = 0, second = 0)
    if (now < start) and (now > finish):
        return True
    return False

if __name__ == '__main__':
    last_sample = None
    current_sample = None
    camera = None
    while True:
        # If there's a video available then just
        # stop filming
        if should_be_sleeping() or video_available():
            if camera is not None:
                camera.cleanup()
                camera = None
            time.sleep(10)
            continue

        # Setup the camera
        if camera is None:
            camera = camera_manager.CameraManager()
            camera.setup()
            camera.light(True)

        # Check if we should be filming
        current_sample = get_last_sample()
        video = None
        if is_active(last_sample, current_sample):
            print "Is active, filming"
            video = camera.capture_video()
        else:
            print "Not active"

        time.sleep(13)
        # Update sample
        last_sample = current_sample
        current_sample = get_last_sample()

        # If still active, save
        if is_active(last_sample, current_sample):
            save_video(video, False)
        else:
            discard_video(video)
