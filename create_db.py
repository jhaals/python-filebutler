#!/usr/bin/env python
# Copyright (c) 2011, Johan Haals <johan.haals@gmail.com>
# All rights reserved.

import os
import sqlite3
import ConfigParser as configparser
from password import Password

config = configparser.RawConfigParser()
if not config.read([os.path.expanduser('~/.ppupload.conf') or 'ppupload.conf', '/etc/ppupload.conf']):
    sys.exit("Couldn't read configuration file")
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
            return 'Done'
        else:
            return 'User already exists'
        
    def delete(self, user):
        ''' Delete user from database '''
        if self.exists(user):
             c.execute("""delete from users where username=?""", (user,))
             conn.commit()
             return 'Done'
        else:
            return 'User does not exist'

    def change_password(self, user, password):
        pass

user = User(config.get('settings', 'secret_key'))

# Create user foobar with password 123
#print user.create('foobar', '123')

# Delete user foobar
#user.delete('foobar')

c.close()
