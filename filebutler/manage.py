#!/usr/bin/env python
# Copyright (c) 2011-2012, Johan Haals <johan.haals@gmail.com>
# All rights reserved.

# Standard library
import getpass
import os
import sys
from argparse import ArgumentParser
from ConfigParser import RawConfigParser


def ask(question, yes_no=False):
    while 1:
        if yes_no:
            answer = raw_input(question + '[y/n]: ')
            if answer == 'y':
                return True
            elif answer == 'n':
                return False
            else:
                continue
            break
        if not yes_no:
            answer = raw_input(question + ': ')
        if not len(answer):
            continue
        break
    return answer


def configuration_tutorial():
    print "python-filebutler couldn't detect the configuration file."
    print
    print 'Specify address to the webserver where filebutler is running'
    print "If you want to test locally use: http://127.0.0.1:5000"
    url = ask('url')

    debug = ask('Enable debug mode', yes_no=True)
    if debug:
        debug = 'True'
    else:
        debug = 'False'

    storage_path = ask('Storage directory, where files will be stored')
    if not os.path.isdir(storage_path):
        sys.exit('%s is not a valid storage path' % storage_path)

    database_path = ask(
        'Database path, where sqlite database should be located')

    if not os.path.isdir(database_path):
        sys.exit(
            '%s is not a valid directory for the database' % database_path)
    database_path = os.path.join(database_path, 'filebutler.sqlite')

    print 'Enter a secret key (will be used to encrypt passwords)'
    print 'Type at least 100 random characters.'
    secret_key = ask('Secret Key')
    print
    print 'Storage path:', storage_path
    print 'Database path:', database_path
    print 'Debug:', debug
    print 'URL:', url

    if ask('Is this information correct?', yes_no=True):
        config_path = 'python-filebutler.conf'
        print 'Writing config file to %s' % config_path

        with open(config_path, 'w') as f:
            f.write('[settings]\n')
            f.write('url = %s\n' % url)
            f.write('debug = %s\n' % debug)
            f.write('port = 5000')
            f.write('storage_path = %s\n' % storage_path)
            f.write('database_path = %s\n' % database_path)
            f.write('secret_key = %s\n' % secret_key)
    else:
        # restart tutorial...
        configuration_tutorial()

paths = [
    'python-filebutler.conf',
    '/etc/python-filebutler.conf',
]

config = RawConfigParser()
if not config.read(paths):
    configuration_tutorial()

from fbquery import FbQuery

parser = ArgumentParser(usage='%(prog)s -h')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--add-user',
    metavar='<username>', help='Adds a new user')

group.add_argument('--delete-user',
    metavar='<username>', help='Deletes an existing user')

group.add_argument('--change-password',
    metavar='<username>', help='Change password of an existing user')

group.add_argument('--delete-expired-data',
    action='store_true', help='Delete expired data from database')

options = parser.parse_args()
fb = FbQuery()

if options.add_user:
    password = getpass.getpass('Password:')
    print fb.user_create(options.add_user, password)

if options.delete_user:
    print fb.user_delete(options.delete_user)

if options.change_password:
    password = getpass.getpass('New password: ')
    print fb.user_change_password(options.change_password, password)

if options.delete_expired_data:
    fb.file_remove_expired()
