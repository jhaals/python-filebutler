#!/usr/bin/env python
# Copyright (c) 2011, Johan Haals <johan.haals@gmail.com>
# All rights reserved.

# Standard library
import os
import sqlite3
import ConfigParser as configparser
import getpass
from optparse import OptionParser

# Local
from password import Password
from filevalidity import FileValidity

config = configparser.RawConfigParser()
if not config.read([os.path.expanduser('~/.filebutler.conf'), 'filebutler.conf', '/etc/filebutler.conf']):
    sys.exit("Couldn't read configuration file")

usage = 'usage: %prog -h'
parser = OptionParser(usage)
parser.add_option('--user', '-u', help='Username', default=False)
parser.add_option('--adduser', '-a', help='Add new user', action='store_true', default=False)
parser.add_option('--deleteuser', '-d', help='One time download', action='store_true', default=False)
parser.add_option('--changepassword', help='change user password', action='store_true', default=False)
parser.add_option('--delete-expired-data', help='One time download', default=False, action='store_true')

options, args = parser.parse_args()


conn = sqlite3.connect(config.get('settings', 'database_path'))
c = conn.cursor()

c.execute('''create table if not exists files
(hash text, user_id int, filename text, expire text, one_time_download bool, download_password text)''')

c.execute('''create table if not exists users
(id INTEGER PRIMARY KEY, username text, password text)''')

conn.commit()

class User:
    def __init__(self, secret_key):
        # should connect to sqlite here.
        self.pw = Password(secret_key)

    def exists(self, user):
        ''' check if user exists, return true/false '''
        c.execute("""SELECT id FROM users where username=?""", (user,))
        if c.fetchone() == None:
            return False
        else:
            return True

    def create(self, user, password):
        ''' Add new user to database '''
        if not self.exists(user):
            c.execute("""insert into users (username, password) values (?, ?)""", (user, self.pw.generate(password),))
            conn.commit()
            return 'Added %s' % user
        else:
            return 'User %s already exists' % user

    def delete(self, user):
        ''' Delete user from database '''
        if self.exists(user):
             c.execute("""delete from users where username=?""", (user,))
             conn.commit()
             return 'Deleted %s' % user
        else:
            return 'User %s does not exist' % user

    def change_password(self, user, password):
        if self.exists(user):
            c.execute("""UPDATE users SET password=? WHERE username=?""", (self.pw.generate(password), user,))
            conn.commit()
            return 'Password successfully changed'
        else:
            return 'User %s does not exist' % user

user = User(config.get('settings', 'secret_key'))

if options.adduser:
    if options.user:
        password = getpass.getpass('Password: ')
        print user.create(options.user, password)
    else:
        parser.error('Please specify username')

if options.deleteuser:
    if options.user:
        print user.delete(options.user)
    else:
        parser.error('Please specify username')

if options.changepassword:
    if options.user:
        password = getpass.getpass('New password: ')
        print user.change_password(options.user, password)
    else:
        parser.error('Please specify username')
if options.delete_expired_data:
    #fw = FileValidity
    print 'yes'
c.close()
