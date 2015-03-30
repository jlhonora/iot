#!/usr/bin/python

import httplib
import httplib2
import os
import random
import sys
import time
import datetime
import argparse

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client import tools
from oauth2client.tools import run_flow


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead, httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady, httplib.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = "youtube_client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, options):
  tags = None
  if options.keywords:
    tags = options.keywords.split(",")

  body=dict(
    snippet=dict(
      title=options.title,
      description=options.description,
      tags=tags
    ),
    status=dict(
      privacyStatus=options.privacyStatus
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time.
    media_body=MediaFileUpload(options.file, chunksize=1048576, resumable=True)
  )

  return resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print "Uploading file..."
      status, response = insert_request.next_chunk()
      if 'id' in response:
        print "Video id '%s' was successfully uploaded." % response['id']
        return str("youtu.be/%s" % str(response['id']))
      else:
        exit("The upload failed with an unexpected response: %s" % response)
    except TypeError:
        error = "Unknown error, response: %s" % str(response)
    except HttpError, e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS, e:
      error = "A retriable error occurred: %s" % e

    if error is not None:
      print error
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print "Sleeping %f seconds and then retrying..." % sleep_seconds
      time.sleep(sleep_seconds)

def convert_video(filename):
  filename_no_ext = os.path.splitext(filename)[0]
  print "Converting %s.h264 to %s.mp4" % (filename_no_ext, filename_no_ext)
  # No need to use avconv for now
  # os.popen("avconv -y -r 30 -i %s.h264 -vcodec copy %s.mp4" % (filename_no_ext, filename_no_ext))
  # Just copying the file does the trick
  os.popen("cp %s.h264 %s.mp4" % (filename_no_ext, filename_no_ext))

  return filename_no_ext + ".mp4"

def upload_video(filename):
  if filename is None:
    return
  if ".h264" in filename:
    filename = convert_video(filename)
  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser],
      conflict_handler = 'resolve')
  parser.add_argument("--file", default = filename)
  parser.add_argument("--title", default = "Antu the Hedgehog running (%s)" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
  parser.add_argument("--description", default = "twitter.com/runhedgie , github.com/jlhonora , honorato.org")
  parser.add_argument("--keywords", default = "Animals, Hedgehog, Raspberry Pi, Infrared")
  parser.add_argument("--privacyStatus", default = "public")
  args = parser.parse_args()
  args.noauth_local_webserver = True

  if not os.path.exists(args.file):
    exit("Please specify a valid file using the --file= parameter.")

  youtube = get_authenticated_service(args)
  try:
    return initialize_upload(youtube, args)
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
    return None

if __name__ == '__main__':
  result = upload_video("assets/video.h264")
  print "Uploaded: %s" % str(result)
