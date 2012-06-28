#!/usr/bin/env python
# Copyright (c) 2011-2012, Johan Haals <johan.haals@gmail.com>
# All rights reserved.

# Standard library
import getpass
from optparse import OptionParser

# Local
from fbquery import FbQuery

usage = 'usage: %prog -h'
parser = OptionParser(usage)
parser.add_option('--user', '-u', help='Username', default=False)
parser.add_option('--add-user',
    '-a', help='Add new user', action='store_true', default=False)
parser.add_option('--delete-user',
    '-d', help='Delete user', action='store_true', default=False)
parser.add_option('--change-password',
        help='change user password', action='store_true', default=False)
parser.add_option('--delete-expired-data',
        help='Delete all expired data from database',
        default=False, action='store_true')

options, args = parser.parse_args()

fb = FbQuery()

if options.add_user:
    if options.user:
        password = getpass.getpass('Password: ')
        print fb.user_create(options.user, password)
    else:
        parser.error('Please specify username')

if options.delete_user:
    if options.user:
        print fb.user_delete(options.user)
    else:
        parser.error('Please specify username')

if options.change_password:
    if options.user:
        password = getpass.getpass('New password: ')
        print fb.user_change_password(options.user, password)
    else:
        parser.error('Please specify username')
if options.delete_expired_data:
    fb.file_remove_expired()
