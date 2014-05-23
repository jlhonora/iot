#!/usr/bin/env python
import schedule
import time
import datetime
import twitter
import yaml
import psycopg2
import sensor
import random

def get_random_phrase():
	phrases = ["Yesterday I ran %.1f kms!", "Last night I went jogging for %.1f kms :)", "I'm going to sleep after running %.1f kms"]
	return random.choice(phrases)

def get_low_activity_phrase():
	phrases = ["Lazy day yesterday, just %.1f", "Didn't feel like running yesterday, I did only %.1f kms"]
	return random.choice(phrases)
	
def get_no_activity_phrase():
	phrases = ["Ooops, no running yesterday. @jlhonora, is everything fine?", "I always run, but the system is not working >:|. It's @jlhonora's fault"]
	return random.choice(phrases)

def get_distance_for_date(date):
	print "Getting ran distance for " + str(date)
	with psycopg2.connect("dbname=pgtest2db user=pgtest2user") as dbconn:
		with dbconn.cursor() as cursor:
			counter = sensor.Sensor.get_by_name(cursor, "Antu Counter")
			# Get all measurements betweeen the date and one day before
			cursor.execute("SELECT value FROM measurements WHERE (sensor_id = (%s)) AND (created_at BETWEEN (%s) AND (%s))", (counter.id, date - datetime.timedelta(days = 1), date ))
			meas = cursor.fetchall()
			if meas is None or len(meas) < 2:
				return 0.0;
			# The result is an array of tuples
			return (meas[-1][0] - meas[0][0])

def get_twitter_api():
	with open('twitter_api_config.yaml', 'r') as f:
		doc = yaml.load(f)
		# Setup API
		api = twitter.Api(consumer_key=doc['consumer_key'], consumer_secret=doc['consumer_secret'], access_token_key=doc['access_token_key'], access_token_secret=doc['access_token_secret'])
		print api.VerifyCredentials()
		return api
	return None

def tweet(notFake = True):
	distance = get_distance_for_date(datetime.date.today())
	phrase = ""
	if (distance < 0.001) or (distance > 15.0):
		phrase = get_no_activity_phrase()
	elif distance < 0.8:
		phrase = get_low_activity_phrase()
		phrase = phrase % distance
	else:
		phrase = get_random_phrase()
		phrase = phrase % distance
	api = get_twitter_api()
	if notFake:
		status = api.PostUpdate(phrase)
		print "Posted update with status: " + str(status)
	else:
		print phrase

def test():
	get_twitter_api()
	tweet(False)
	
if __name__ == '__main__':

	test()

	# Schedule job
	schedule.every().day.at("07:30").do(tweet)

	while True:
		schedule.run_pending()
		# Sleep two minutes
		time.sleep(120)
