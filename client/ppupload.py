#!/usr/bin/env python
# Copyright (c) 2011, Johan Haals <johan.haals@gmail.com>
# All rights reserved.

import os
import sys
import ConfigParser as configparser
import requests
from os.path import join
from datetime import datetime
from optparse import OptionParser
from poster.encode import multipart_encode
from datetime import datetime, timedelta

config = configparser.RawConfigParser()
if not config.read([os.path.expanduser('~/.ppupload.conf') or 'ppupload.conf', '/etc/ppupload.conf']):
    sys.exit("Couldn't read configuration file")

usage = 'usage: %prog -h'
parser = OptionParser(usage, version="%prog 0.1")
parser.add_option("--onetime", "-1", help='One time download(optional)', default=False, action='store_true')
parser.add_option("--lifetime", "-l", help='Lifetime(optional): 1h, 1d, 1w, 1m (hour/day/week/month). Default lifetime is unlimited')
parser.add_option("--password", "-p", help='Download password(optional)')

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
        sys.exit('Could not open %s') % content
    filename = os.path.basename(content)

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
    def __init__(self, microseconds=1000000):
        self.started_at = None
        self.timeout = microseconds
        self.previous_length = 0

    def __call__(self, param, current, total):
        if self.started_at is None:
            self.started_at = datetime.now()
        else:
            if datetime.now() - self.started_at > timedelta(microseconds=self.timeout):
                line = '{filename} {percent:.1%}'.format(
                    filename = param.name,
                    percent = current / float(total)
                )

                sys.stdout.write('\b' * self.previous_length)
                sys.stdout.write(line)
                sys.stdout.flush()

                self.previous_length = len(line)
                self.started_at = datetime.now()

half_a_second = 500000

# combine all data before posting
postdata = {
    'file': upload_file,
    'username': config.get('settings', 'username'),
    'password': config.get('settings', 'password'),
    'filename': filename,
    'download_password': download_password,
    'one_time_download': one_time_download,
    'expire': expire
}
datagen, headers = multipart_encode(postdata,
    cb = ProgressMeter(half_a_second)
)

r = requests.post(config.get('settings', 'upload_url'), data=datagen, headers=headers)
print r.content
# parse results from server....

#    download_url = config.get('remote', 'url')+download_hash
#    if sys.platform == 'darwin':
#        os.system('echo %s | pbcopy' % download_url)
#    print download_url
