#!/usr/bin/env python

import os
import sys
import ConfigParser as configparser
import requests
from optparse import OptionParser
from poster.encode import multipart_encode
from datetime import datetime, timedelta
from clipboard import Clipboard

config = configparser.RawConfigParser()
if not config.read([os.path.expanduser('~/.ppupload.conf') or 'ppupload.conf', '/etc/ppupload.conf']):
    sys.exit("Couldn't read configuration file")

usage = 'usage: %prog -h'
parser = OptionParser(usage, version="%prog 0.1")
parser.add_option("--onetime", "-1", help='One time download', default=False, action='store_true')
parser.add_option("--lifetime", "-l", help='Lifetime: 1h, 1d, 1w, 1m (hour/day/week/month). Default lifetime is unlimited')
parser.add_option("--password", "-p", help='Download password')

(options, args) = parser.parse_args()


# file validation
# TODO
#   Add support for multiple files
try:
    content = args[0]
except IndexError:
    parser.error('Specify file to upload')
if not os.path.isfile(content):
    sys.exit('File does not exist')
else:
    try:
        upload_file = open(content, 'rb')
    except IOError:
        sys.exit('Could not open %s' % content)

if options.onetime:
    one_time_download = '1'
else:
    one_time_download = '0'

# Hash download password in case we want some extra security
if options.password:
    download_password = options.password
else:
    download_password = ''

expire = ''
if options.lifetime in ['1h', '1d', '1w', '1m']:
    expire = options.lifetime

class ProgressMeter(object):
    '''
    Prints some data about the upload process.

    It currently updates once per second with filename, the progress expressed
    in percents, and the average transfer speed.
    '''

    def __init__(self):
        self.started = None
        self.previous_update = None
        self.previous_output = ''

    def __call__(self, param, current, total):
        now = datetime.now()

        # Is this the first time we're getting called?
        if self.previous_update is None:
            self.started = now
            self.previous_update = self.started

        # Update once per second
        if now - self.previous_update > timedelta(seconds=1):
            delta = now - self.started

            output = '{filename} {percent:.1%} {speed:.0f} KiB/s'.format(
                filename = param.name,
                percent = current / float(total),
                speed = current / float(delta.seconds) / 1024.0
            )

            sys.stdout.write('\r' + output)

            # If the previous output was longer than our current, we must "pad"
            # our output with spaces to prevent characters from the old output
            # to show up.
            output_delta = len(self.previous_output) - len(output)
            if output_delta > 0:
                sys.stdout.write(' ' * output_delta)

            sys.stdout.flush()

            self.previous_update = now

# combine all data before posting
postdata = {
    'file': upload_file,
    'username': config.get('settings', 'username'),
    'password': config.get('settings', 'password'),
    'download_password': download_password,
    'one_time_download': one_time_download,
    'expire': expire
}

datagen, headers = multipart_encode(postdata,
    cb = ProgressMeter()
)

r = requests.post(config.get('settings', 'upload_url'), data=datagen, headers=headers)

# copy result to clipboard
# TODO
#   this should really be parsed and no text should be copied if r.content contains anything else then a http address.
copy = Clipboard()
copy.set(r.content)

print r.content
