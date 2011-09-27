#!/usr/bin/env python

# Standard Library
import os
import sqlite3
from datetime import datetime

# Third party
from dateutil.relativedelta import relativedelta

class FileValidity:
    def __init__(self, database_path, storage_path):
        ''' connect to database '''
        self.database_path = database_path
        self.storage_path = storage_path
        self.conn = sqlite3.connect(database_path)
        self.c = self.conn.cursor()

    def expired(expire, expire_date):
        expire_date = datetime.strptime(expire_date, '%Y%m%d%H%M%S')

        if datetime.now() > expire_date:
            # Expired
            return True
        else:
            return False

    def remove_expired_files(self):
        ''' remove all expired files from database '''

        self.c.execute("select hash, expire, one_time_download, filename, download_password from files where expire !=0")
        for entry in self.c.fetchall():
            download_hash, expire_date, one_time_download, filename, download_password = entry

            if self.expired(expire_date):
                print 'removed %s' % filename
                self.remove_data(download_hash, filename)

    def remove_data(self, download_hash, filename):
        ''' remove file from storage and database '''

        try:
            os.remove(os.path.join(self.storage_path, download_hash, filename))
            os.removedirs(os.path.join(self.storage_path, download_hash))
        except OSError as e:
            print 'Failed to remove file %s' % e
        
        self.c.execute("delete from files where hash=?", (download_hash,))
        self.conn.commit()
