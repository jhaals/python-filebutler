#!/usr/bin/env python
# Copyright (c) 2011, Johan Haals <johan.haals@gmail.com>
# All rights reserved.

import os
import hashlib
import sqlite3
import re
import ConfigParser as configparser
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime

config = configparser.RawConfigParser()
if not config.read([os.path.expanduser('~/.ppupload.conf') or 'ppupload.conf', '/etc/ppupload.conf']):
    sys.exit("Couldn't read configuration file")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.get('settings', 'storage_path')
app.config['DATABASE'] = config.get('settings', 'database_path')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        
        username = request.form['username']
        password = request.form['password']

        # Validate username and password hash
        # pasword (hash + salt)
        if re.search('[^A-Za-z0-9_]', username):
            return 'Illigal username'
        if re.search('[^A-Za-z0-9_]', password):
            return 'Illigal password'

        # connect to sqlite and check if user exists
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        # We should add some salt here.
        c.execute("select user_id from users where username='%s' and password='%s'" % (username, password))
        result = c.fetchone()

        if result == None:
            return 'Unknown user'

        userid = result[0]

        allowed_expires = {
            '1h': datetime.now() + relativedelta(hours=1),
            '1d': datetime.now() + relativedelta(days=1),
            '1w': datetime.now() + relativedelta(weeks=1),
            '1m': datetime.now() + relativedelta(months=1),
        }

        if request.form['expire'] in allowed_expires:
            expire = allowed_expires[request.form['expire']].strftime('%Y%m%d%H%M')
        else:
            expire = '0'

        one_time_download = '0'

        # Generate download hash
        filename = secure_filename(request.form['filename'])
        download_hash = hashlib.md5(filename+datetime.now().strftime('%f')).hexdigest()

        # Create a directory based on download_hash and save uploaded file to that folder
        try:
            os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], download_hash))
        except IOError:
            return 'Could not upload file'
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], download_hash, filename))

        # save info to database
        c.execute("""insert into files (hash, user_id, filename, expire, one_time_download)
          values ('%s','%s','%s','%s', '%s')""" % (download_hash, userid, filename, expire, one_time_download)) 
        conn.commit()
        c.close()

        # everything ok, return download url to client
        return download_hash

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/download', methods=['GET'])
def download_file():

    download_hash = request.args.get('u')

    if re.search('[^A-Za-z0-9_]', download_hash):
        return 'invalid download hash'

    # connect to sqlite and check if file exists
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute("select expire, one_time_download from files where hash='%s' limit 1" % download_hash)
    result = c.fetchone()

    # No result from query
    if result == None:
        return 'Unknown download hash'
    
    # Everything is OK, serve file [how... train wifi == no documentation]
    return result[0]
    
if __name__ == "__main__":
    app.run(debug=True)

