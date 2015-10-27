#!/usr/bin/env python
import schedule
import time
import datetime
import twitter
import yaml
import psycopg2
import sensor
import random
import math
import os

# Convert the distance to a unit-agnostic reference
# Returns a unit (int) and a reference name (string)
def get_reference_from_distance(distance):
    elements = []
    elements = elements + [('Eiffel Towers', 0.324)]
    elements = elements + [('Empire States', 0.443)]
    elements = elements + [('Central Parks', 4.0)]
    elements = elements + [('Golden Gates', 2.7)]
    elements = elements + [('Burj Khalifa towers', 0.828)]
    elements = elements + [('laps around the Colosseum', 0.527)]
    elements = elements + [('Rubgy fields', 0.118)]
    elements = elements + [('Soccer fields', 0.120)]
    element = random.choice(elements)
    units = distance / element[1]
    if units > 1.5:
        units = str(int(round(units)))
    else:
        units = str("%.1f" % units)
    return units, element[0]

def get_reference_from_distance_test():
    [units, reference] = get_reference_from_distance(0.1)
    print get_random_phrase(0.1)
    [units, reference] = get_reference_from_distance(1.0)
    print get_random_phrase(1.0)
    if reference == 'Eiffel Towers':
        assert units == str(3)
    elif reference == 'Empire States':
        assert units == str(2)
    elif reference == 'Central Parks':
        assert units == str(0.3)
    [units, reference] = get_reference_from_distance(5.0)
    print get_random_phrase(5.0)
    if reference == 'Eiffel Towers':
        assert units == str(15)
    elif reference == 'Empire States':
        assert units == str(11)
    elif reference == 'Central Parks':
        assert units == str(1.3)

def get_random_phrase(distance):
    phrases = []
    [units, reference] = get_reference_from_distance(distance)
    phrases = phrases + ["Yesterday I ran %.1f km. That's like %s %s!" % (distance, units, reference)]
    phrases = phrases + ["Last night I went jogging for %.1f km, that's about %s %s :)" % (distance, units, reference)]
    phrases = phrases + ["I'm going to sleep after running %.1f km. That's almost %s %s!" % (distance, units, reference)]
    phrases = phrases + ["Really happy (and a bit tired) after running %s %s :O (%.1f km)" % (units, reference, distance)]
    phrases = phrases + ["Fast as Sonic. %.1f km last night, whoa!" % distance]
    phrases = phrases + ["Just completed a %.1f km run with #AntuKeeper, keep up!" % distance]
    phrases = phrases + ["Treading light for %.1f km, good night :)" % distance]
    return random.choice(phrases)

def get_weekly_phrase(distance):
    return "Last week I ran %.f km!" % distance

def get_low_activity_phrase(distance):
    phrases = ["Lazy day yesterday, just %.1f km" % distance, "Didn't feel like running yesterday, I did only %.1f km" % distance]
    return random.choice(phrases)
    
def get_no_activity_phrase(distance):
    phrases = ["Ooops, no running yesterday. @jlhonora, is everything fine?", "I always run, but the system is not working >:|. It's @jlhonora's fault"]
    return random.choice(phrases)

def get_laps_for_date(date):
    print "Getting ran laps for " + str(date)
    with psycopg2.connect("dbname=pgtest2db user=pgtest2user") as dbconn:
        with dbconn.cursor() as cursor:
            counter = sensor.Sensor.get_by_name(cursor, "Antu Counter")
            # Get all measurements betweeen the date and one day before
            start_date = date - datetime.timedelta(days = 1)
            end_date = date
            print "Querying from " + str(start_date) + " to " + str(end_date)
            cursor.execute("SELECT value FROM measurements WHERE (sensor_id = (%s)) AND (created_at BETWEEN (%s) AND (%s))", (counter.id, start_date, end_date))
            meas = cursor.fetchall()
            print "0: " + str(meas[0][0])
            print "1: " + str(meas[-1][0])
            if meas is None or len(meas) < 2:
                return 0.0;
            # The result is an array of tuples
            return (meas[-1][0] - meas[0][0])

def laps2km(laps):
    return (laps * (2.0 * math.pi * 0.14)) / 1000.0;

def get_last_battery():
    with psycopg2.connect("dbname=pgtest2db user=pgtest2user") as dbconn:
        with dbconn.cursor() as cursor:
            counter = sensor.Sensor.get_by_name(cursor, "Battery")
            cursor.execute("SELECT value FROM measurements WHERE (sensor_id = (%s)) ORDER BY id DESC LIMIT 1", (counter.id,))
            meas = cursor.fetchall()
            print "0: " + str(meas[0][0])
            return meas[0][0]
    

def get_twitter_api():
    with open('twitter_api_config.yml', 'r') as f:
        doc = yaml.load(f)
        # Setup API
        api = twitter.Api(consumer_key=doc['consumer_key'], consumer_secret=doc['consumer_secret'], access_token_key=doc['access_token_key'], access_token_secret=doc['access_token_secret'])
        print api.VerifyCredentials()
        return api
    return None

def tweet(notFake = True, base = datetime.datetime.utcnow(), allowPast = False):
    if not allowPast:
        base = datetime.datetime.utcnow()
    laps = get_laps_for_date(base)
    print "Laps: %.1f" % laps
    distance = laps2km(laps)
    print "Distance: %.1f km" % distance
    phrase = ""
    if distance > 22.5:
        distance = 0.0
    if (distance < 0.05):
        phrase = get_no_activity_phrase(distance)
    elif distance < 0.9:
        phrase = get_low_activity_phrase(distance)
    else:
        phrase = get_random_phrase(distance)

    phrase = include_video(phrase)
    print "Phrase: %s" % phrase

    perform_update(phrase, notFake)

def weekly_tweet(notFake = True, base = datetime.datetime.utcnow()):
    laps = get_laps_for_timerange(base - datetime.timedelta(days=7), base)
    print "Laps: %.1f" % laps
    distance = laps2km(laps)
    print "Distance: %.1f km" % distance
    phrase = get_weekly_phrase(distance)
    if notFake:
        api = get_twitter_api()
        status = api.PostUpdate(phrase)
        print "Posted update with status: " + str(status)
    else:
        print phrase

def include_video(phrase, filename = 'video.yml'):
    # TODO: Remove video
    video, should_remove_file = get_video(filename)
    if video is None:
        return phrase
    final_phrase = " ".join([phrase, video])
    if len(final_phrase) > 140:
        remove_file(filename)
        return phrase
    remove_file(filename)
    return final_phrase

def get_video(filename = 'video.yml'):
    if not os.path.exists(filename):
        print "No video file, returning"
        return None, False
    should_remove_file = True
    with open(filename, 'r') as f:
        doc = None
        try:
            doc = yaml.load(f)
        except (yaml.parser.ParserError, yaml.scanner.ScannerError):
            print "Invalid yaml file"

        if doc is None:
            should_remove_file = True
        if 'uploaded' not in doc:
            print "No 'uploaded' flag"
        elif doc['uploaded'] != "True":
            print "Video not uploaded"
            should_remove_file = False
        elif 'url' not in doc or len(doc['url'].strip()) <= 0:
            print "Invalid url, returning"
        else:
            return doc['url'], False
    return None, should_remove_file

def tweet_video(filename = 'video.yml', notFake = True):
    print "Attempting video upload"
    video, should_remove_file = get_video(filename)
    if video is not None:
        print "Tweeting video %s" % video
        api = get_twitter_api()
        if notFake:
            api.PostDirectMessage("Video is %s" % video, screen_name="jlhonora")
        remove_file(filename)

def remove_file(filename):
    print "Removing file %s" % filename
    if filename is None:
        return
    try:
        os.remove(filename)
    except OSError, e:
        print "Couldn't remove file %s" % str(filename)

def check_battery(notFake = True):
    battery = get_last_battery()
    print "Battery: %.3f" % battery
    if battery > 3.85:
        print "Battery OK"
    else:
        print "Battery low!"
        if notFake:
            api = get_twitter_api()
            status = api.PostUpdate("@jlhonora Battery is running low")
            print "Posted update with status: " + str(status)
        else:
            print phrase

def retry_loop(status, maxRetries = 7):
    retries = 0
    while retries < maxRetries:
        try:
            api = get_twitter_api()
            status = api.PostUpdate(status)
            print "Posted update with status: " + str(status)
            return
        except:
            retries = retries + 1
            delay = retries ** 4 + 15
            print "Error while tweeting, retrying in %d seconds" % delay
            time.sleep(delay)

def perform_update(status, notFake = True, maxRetries = 7):
    if notFake:
        retry_loop(status, maxRetries)
    else:
        print status

def test():
    get_twitter_api()
    tweet_video(notFake=False)
    get_reference_from_distance_test()
    tweet(False, datetime.datetime.strptime('2015-10-27 11:00:00', '%Y-%m-%d %H:%M:%S'), True)
    check_battery(False)
    #retry_loop("Test")
    
if __name__ == '__main__':
    random.seed(str(datetime.datetime.now()))

    # test()

    # Schedule job
    schedule.every().day.at("11:00").do(tweet)
    #schedule.every().day.at("11:00").do(tweet_video)
    #schedule.every().monday.at("10:50").do(weekly_tweet)
    #schedule.every().day.do(attempt_monthly_tweet)
    #schedule.every().day.at("22:00").do(check_battery)

    while True:
        schedule.run_pending()
        # Sleep 30 seconds
        time.sleep(30)
