#!/usr/bin/env python

# Standard Library
import os
import sqlite3
import ConfigParser as configparser
from datetime import datetime

# Third party
from dateutil.relativedelta import relativedelta

config = configparser.RawConfigParser()
if not config.read([os.path.expanduser('~/.ppupload.conf') or 'ppupload.conf', '/etc/ppupload.conf']):
    sys.exit("Couldn't read configuration file")

# connect to sqlite and check if file exists
conn = sqlite3.connect(config.get('settings', 'database_path'))
c = conn.cursor()
c.execute("select hash, expire, one_time_download, filename, download_password from files where expire !=0")

for entry in c.fetchall():
    download_hash, expire, one_time_download, filename, download_password = entry

    expire = datetime.strptime(expire, '%Y%m%d%H%M')
    if datetime.now() > expire:
        try:
            os.remove(os.path.join(config.get('settings', 'storage_path'), download_hash, filename))
            os.removedirs(os.path.join(config.get('settings', 'storage_path'), download_hash))
        except OSError as e:
            print 'Failed to remove files %s' % e

        c.execute("delete from files where hash=?", (download_hash,))
        conn.commit()
        c.close()
