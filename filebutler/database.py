#!/usr/bin/env python
# Copyright (c) 2011-2012, Johan Haals <johan.haals@gmail.com>
# All rights reserved.

import peewee
import ConfigParser as configparser
import sys

config = configparser.RawConfigParser()
if not config.read('filebutler.conf'):
        sys.exit("Couldn't read configuration file")

db = peewee.SqliteDatabase(config.get('settings', 'database_path'))


class CustomModel(peewee.Model):
    class Meta:
        database = db


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

    def __unicode__(self):
        return self.hash
