#!/usr/bin/env python
# Copyright (c) 2011-2012, Johan Haals <johan.haals@gmail.com>
# All rights reserved.

# Standard Library
import os
import hashlib
import re
import sys
import ConfigParser as configparser
from datetime import datetime

# Third party
from flask import Flask, request, send_from_directory, render_template, jsonify
from werkzeug import secure_filename
from dateutil.relativedelta import relativedelta

# Local
from password import Password
from fbquery import FbQuery

config = configparser.RawConfigParser()
if not config.read('/etc/filebutler.conf'):
    sys.exit("Couldn't read configuration file")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.get('settings', 'storage_path')
app.config['DATABASE'] = config.get('settings', 'database_path')
app.config['URL'] = config.get('settings', 'url')


def json_response(message, status_code):
    # Convert return message to json, add status_code
    response = jsonify(message=message)
    response.status_code = status_code
    return response


@app.route('/', methods=['POST'])
def upload_file():
    file = request.files['file']
    username = request.form['username']
    password = request.form['password']
    download_password = request.form['download_password']
    expire = '0'
    one_time_download = False

    fb = FbQuery()

    if not fb.user_exist(username):
        return json_response('Could not find user', 401)

    u = fb.user_get(username)
    pw = Password(config.get('settings', 'secret_key'))

    if not pw.validate(u.password, password):
        return json_response('Invalid username/password', 401)

    allowed_expires = {
        '1h': datetime.now() + relativedelta(hours=1),
        '1d': datetime.now() + relativedelta(days=1),
        '1w': datetime.now() + relativedelta(weeks=1),
        '1m': datetime.now() + relativedelta(months=1),
        }

    if request.form['expire'] in allowed_expires:
        expire = allowed_expires[request.form['expire']].strftime('%Y%m%d%H%M%S')

    if request.form['one_time_download'] == '1':
        one_time_download = True

    if download_password:
        download_password = pw.generate(download_password)

    # Generate download hash
    filename = secure_filename(os.path.basename(file.filename))
    download_hash = hashlib.sha1(
        filename + datetime.now().strftime('%f')).hexdigest()

    # Create a directory based on hash and save file to that folder
    try:
        os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], download_hash))
    except OSError:
        return json_response(
                'Could not upload file(storage directory does not exist)', 500)

    file.save(os.path.join(app.config['UPLOAD_FOLDER'],
        download_hash,
        filename))

    fb.file_add(download_hash, u.id, filename, expire,
        one_time_download, download_password)

    # everything ok, return download url to client
    return json_response(
            ''.join([app.config['URL'], '/download?u=', download_hash]), 200)


@app.route('/download', methods=['GET', 'POST'])
def download_file():

    download_hash = request.args.get('u')

    if not download_hash:
        return 'No download hash specified'

    if re.search('[^A-Za-z0-9_]', download_hash):
        return 'invalid download hash'

    fb = FbQuery()
    # fetch file
    f = fb.file_get(download_hash)

    if not f:
        return 'Could not find file'

    if f.expire != '0':
        # Expire date exists
        if fb.file_expired(f.expire):
            # Remove expired file from storage and database
            fb.file_remove(download_hash, f.filename)
            return 'This download has expired'

    if f.download_password:
        # This file is password protected.
        if request.method == 'POST':
            # Validate download_password from database with user input
            pw = Password(config.get('settings', 'secret_key'))
            if not pw.validate(f.download_password, request.form['password']):
                return render_template('download.html',
                        error='Invalid Password')

        else:
            return render_template('download.html', error=None)

    if f.one_time_download == 1:
        # Set expire date to current time, download will be invalid in a minute
        fb.file_set_expiry(download_hash,
                datetime.now().strftime('%Y%m%d%H%M%S'))

    # Serve file, everything is ok
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'],
        download_hash),
        f.filename,
        as_attachment=True)

if __name__ == "__main__":
    app.run(debug=config.get('settings', 'debug'),
            port=int(config.get('settings', 'port')))
