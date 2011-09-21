#!/usr/bin/env python

# Standard Library
import os
import hashlib
import sqlite3
import re
import sys
import ConfigParser as configparser
from datetime import datetime

# Third party
from flask import Flask, request, send_from_directory
from werkzeug import secure_filename
from dateutil.relativedelta import relativedelta

# Local
from password import Password

config = configparser.RawConfigParser()
if not config.read([os.path.expanduser('~/.filebutler.conf') or 'filebutler.conf', '/etc/filebutler.conf']):
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
        download_password = request.form['download_password']
        expire = '0'
        one_time_download = '0'
        
        # connect to sqlite and check if user exists
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        c.execute("select id, password from users where username=?", (username,))
        
        try:
            user_id, password_hash = c.fetchone()
        except TypeError:        
            return 'Error: Check username/password'
        
        pw = Password(config.get('settings', 'secret_key'))

        if not pw.validate(password_hash,password):
            return 'Invalid username/password'
        
        allowed_expires = {
            '1h': datetime.now() + relativedelta(hours=1),
            '1d': datetime.now() + relativedelta(days=1),
            '1w': datetime.now() + relativedelta(weeks=1),
            '1m': datetime.now() + relativedelta(months=1),
        }

        if request.form['expire'] in allowed_expires:
            expire = allowed_expires[request.form['expire']].strftime('%Y%m%d%H%M%S')
            
        if request.form['one_time_download'] == '1':
            one_time_download = '1'

        if download_password:
            download_password = pw.generate(download_password)

        # Generate download hash
        filename = secure_filename(os.path.basename(file.filename))
        download_hash = hashlib.sha1(filename+datetime.now().strftime('%f')).hexdigest()

        # Create a directory based on download_hash and save uploaded file to that folder
        try:
            os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], download_hash))
        except OSError:
            return 'Could not upload file(storage directory does not exist)'

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], download_hash, filename))

        # save info to database
        insert_data = (download_hash, user_id, filename, expire, one_time_download, download_password,)
        c.execute("""insert into files (hash, user_id, filename, expire, one_time_download, download_password)
          values (?,?,?,?,?,?)""", insert_data)
        conn.commit()
        c.close()

        # everything ok, return download url to client
        return config.get('settings', 'url')+download_hash

    # TODO
    #   web interface...
    return 'Only POSTING allowed'

@app.route('/download', methods=['GET', 'POST'])
def download_file():

    download_hash = request.args.get('u')

    if not download_hash:
        return 'No download hash specified'

    if re.search('[^A-Za-z0-9_]', download_hash):
        return 'invalid download hash'

    # connect to sqlite and check if file exists
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute("select expire, one_time_download, filename, download_password from files where hash=? limit 1", (download_hash,))

    try:
        expire, one_time_download, filename, download_password = c.fetchone()
    except TypeError:
        # No result from query
        return 'Unknown download hash'

    # Check expire date (if any)
    if expire != '0':
        expire = datetime.strptime(expire, '%Y%m%d%H%M%S')
        if datetime.now() > expire:
            # Download has expired, remove file and database entry
            # TODO
            #   create a function since this will be used if one_time_download is set to 1 
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], download_hash, filename))
            os.removedirs(os.path.join(app.config['UPLOAD_FOLDER'], download_hash))
            c.execute("delete from files where hash=?", (download_hash,))
            conn.commit()
            c.close()
            return 'This download has expired'

    if download_password:
        # This file is password protected.
        if request.method == 'POST':
            # Validate download_password from database with user input
            pw = Password(config.get('settings', 'secret_key'))
            if not pw.validate(download_password,request.form['password']):
                return 'Invalid password'
        else:
            return '''
            <!doctype html>
            <title>Download file</title>
            <h1>Upload new File</h1>
            <form action="" method="post">
            <p><input type="password" name="password">
            <input type="submit" value="Download">
            </form>
            '''
    if one_time_download == 1:
        # Set expire date to current time, download will be invalid in a minute
        insert_data = (datetime.now().strftime('%Y%m%d%H%M%S'), download_hash,)
        c.execute("""UPDATE files SET expire=? WHERE  hash=?""", insert_data)
        conn.commit()
        c.close()

    # Serve file, everything is ok
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], download_hash),
                               filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=config.get('settings', 'debug'),port=int(config.get('settings', 'port')))
