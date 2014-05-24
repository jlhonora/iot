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

# Convert the distance to a unit-agnostic reference
# Returns a unit (int) and a reference name (string)
def get_reference_from_distance(distance):
	elements = []
	elements = elements + [('Eiffel Towers', 0.324)]
	elements = elements + [('Empire States', 0.443)]
	elements = elements + [('Central Parks', 4.0)]
	element = random.choice(elements)
	units = distance / element[1]
	if units > 1.0:
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
		assert units == str(1)

def get_random_phrase(distance):
	phrases = []
	[units, reference] = get_reference_from_distance(distance)
	phrases = phrases + ["Yesterday I ran %.1f km. That's like %s %s!" % (distance, units, reference)]
	phrases = phrases + ["Last night I went jogging for %.1f km, that's about %s %s :)" % (distance, units, reference)]
	phrases = phrases + ["I'm going to sleep after running %.1f km. That's almost %s %s!" % (distance, units, reference)]
	phrases = phrases + ["Really happy (and a bit tired) after running %s %s :O (%.1f km)" % (units, reference, distance)]
	phrases = phrases + ["Fast as Sonic. %.1f km last night, whoa!" % distance]
	phrases = phrases + ["Just completed a %.1f km run with #AntuKeeper, keep up!" % distance]
	phrases = phrases + ["Treading light for %.f km, good night pals :)" % distance]
	return random.choice(phrases)

def get_low_activity_phrase(distance):
	phrases = ["Lazy day yesterday, just %.1f", "Didn't feel like running yesterday, I did only %.1f km"]
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

def get_twitter_api():
	with open('twitter_api_config.yaml', 'r') as f:
		doc = yaml.load(f)
		# Setup API
		api = twitter.Api(consumer_key=doc['consumer_key'], consumer_secret=doc['consumer_secret'], access_token_key=doc['access_token_key'], access_token_secret=doc['access_token_secret'])
		print api.VerifyCredentials()
		return api
	return None

def tweet(notFake = True):
	laps = get_laps_for_date(datetime.datetime.utcnow())
	print "Laps: %.1f" % laps
	distance = laps2km(laps)
	print "Distance: %.1f km" % distance
	phrase = ""
	if (distance < 0.001) or (distance > 15.0):
		phrase = get_no_activity_phrase(distance)
	elif distance < 0.8:
		phrase = get_low_activity_phrase(distance)
	else:
		phrase = get_random_phrase(distance)
	api = get_twitter_api()
	if notFake:
		status = api.PostUpdate(phrase)
		print "Posted update with status: " + str(status)
	else:
		print phrase

def test():
	get_reference_from_distance_test()
	get_twitter_api()
	tweet(False)
	
if __name__ == '__main__':

	# test()

	# Schedule job
	schedule.every().day.at("11:00").do(tweet)

	while True:
		schedule.run_pending()
		# Sleep two minutes
		time.sleep(120)
