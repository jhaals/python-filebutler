#!/usr/bin/env python
# Copyright (c) 2011-2012, Johan Haals <johan.haals@gmail.com>
# All rights reserved.

import peewee
import datetime
import ConfigParser as configparser
import sys

paths = [
    'python-filebutler.conf',
    '/etc/python-filebutler.conf',
]

config = configparser.RawConfigParser()

if not config.read(paths):
        sys.exit("Couldn't read configuration file")


class CustomModel(peewee.Model):
    class Meta:
        database = peewee.SqliteDatabase(config.get('settings', 'database_path'), threadlocals=True)


class User(CustomModel):
    username = peewee.CharField()
    password = peewee.TextField()

    def __unicode__(self):
        return self.username


class File(CustomModel):
    hash = peewee.TextField()
    user = peewee.ForeignKeyField(User)
    filename = peewee.TextField()
    expire = peewee.TextField()
    one_time_download = peewee.BooleanField()
    download_password = peewee.TextField()
    upload_date = peewee.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return self.hash
