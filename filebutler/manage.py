#!/usr/bin/env python
# Copyright (c) 2011-2012, Johan Haals <johan.haals@gmail.com>
# All rights reserved.

# Standard library
import getpass
from argparse import ArgumentParser

# Local
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
