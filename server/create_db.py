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

# THIS IS JUST FOR TESTING DURING DEVELOPMENT. WILL BE REWRITTEN SOON

username = 'jhaals'
password = '123'

pw = Password(config.get('settings', 'secret_key'))

c = conn.cursor()

c.execute('''create table files
(hash text, user_id int, filename text, expire text, one_time_download bool, download_password text)''')

c.execute('''create table users
(id INTEGER PRIMARY KEY, username text, password text)''')

c.execute("""insert into users (username, password) values ('%s', '%s')""" % (username, pw.generate(password)))

conn.commit()
c.close()
