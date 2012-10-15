#!/usr/bin/env python
# Copyright (c) 2011-2012, Johan Haals <johan.haals@gmail.com>
# All rights reserved.

# Standard Library
import os
import hashlib
import re
import sys
import json
import ConfigParser as configparser
from mimetypes import guess_type
from datetime import datetime
from urlparse import urljoin

# Third party
from flask import Flask, request, send_from_directory, render_template, jsonify
from werkzeug import secure_filename
from dateutil.relativedelta import relativedelta

# Local
from password import Password
from fbquery import FbQuery

paths = [
    'python-filebutler.conf',
    '/etc/python-filebutler.conf'
]

config = configparser.RawConfigParser()

if not config.read(paths):
    sys.exit("Couldn't read configuration file")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.get('settings', 'storage_path')
app.config['DATABASE'] = config.get('settings', 'database_path')
app.config['URL'] = config.get('settings', 'url')


def response(request, message, status_code):
    # Convert return message to json, add status_code
    if 'application/json' in request.headers['Accept']:
        response = jsonify(message=message)
        response.status_code = status_code
        return response

    return render_template('message.html', message=message), status_code


def authenticate(fb, pw, username, password):

    user = fb.user_get(username)
    if not user or not pw.validate(user.password, password):
        return None
    return user


@app.route('/', methods=['POST', 'GET'])
def upload_file():

    if request.method == 'GET':
        return render_template('upload.html')

    file = request.files['file']

    if not file.filename:
        return response(request, 'No file selected', 400)

    username = request.form['username']
    password = request.form['password']
    download_password = request.form['download_password']
    expire = '0'
    one_time_download = False

    fb = FbQuery()
    pw = Password(config.get('settings', 'secret_key'))

    user = authenticate(fb, pw, username, password)
    if not user:
        return response(request, 'Invalid username or password', 401)

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
        return response(request,
                'Could not upload file(storage directory does not exist)', 500)

    file.save(os.path.join(app.config['UPLOAD_FOLDER'],
        download_hash,
        filename))

    fb.file_add(download_hash, user.id, filename, expire,
        one_time_download, download_password)

    # everything ok, return download url to client
    return response(request, urljoin(app.config['URL'], download_hash), 200)


@app.route('/<download_hash>/delete', methods=['POST'])
def delete(download_hash):

    username = request.form['username']
    password = request.form['password']

    fb = FbQuery()
    pw = Password(config.get('settings', 'secret_key'))

    if not authenticate(fb, pw, username, password):
        return response(request, 'Invalid username or password', 401)
    f = fb.file_get(download_hash)

    if not f:
        return response(request, 'Could not find file', 410)
    if f.user.username != username:
        return response(request, 'You cant delete this file!', 401)

    if not fb.file_remove(download_hash, f.filename):
        return response(request, 'Could not delete file', 500)

    return response(request, 'File deleted', 200)


@app.route('/<download_hash>', methods=['GET', 'POST'])
def download(download_hash):

    if not download_hash:
        return response(request, 'No download hash specified', 400)

    if re.search('[^A-Za-z0-9_]', download_hash):
        return response(request, 'invalid download hash', 400)

    fb = FbQuery()
    # fetch file
    f = fb.file_get(download_hash)

    if not f:
        return response(request, 'Could not find file', 404)

    if f.expire != '0':
        # Expire date exists
        if fb.file_expired(f.expire):
            # Remove expired file from storage and database
            fb.file_remove(download_hash, f.filename)
            return response(request, 'This download has expired', 410)

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

    if f.one_time_download:
        # Set expire date to current time, download will be invalid in a minute
        fb.file_set_expiry(download_hash,
                datetime.now().strftime('%Y%m%d%H%M%S'))

    # Serve images in browser
    type = guess_type(os.path.join(app.config['UPLOAD_FOLDER'], download_hash, f.filename))[0]
    attachment = True
    if type and 'image' in type:
        attachment = False

    # Serve file, everything is ok
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'],
        download_hash),
        f.filename,
        as_attachment=attachment, cache_timeout=0)


@app.route('/files', methods=['POST'])
def files():

    username = request.form['username']
    password = request.form['password']

    fb = FbQuery()
    pw = Password(config.get('settings', 'secret_key'))

    if not authenticate(fb, pw, username, password):
        return response(request, 'Invalid username or password', 401)

    return json.dumps(fb.user_list_files(username))



if __name__ == "__main__":
    app.run(debug=config.get('settings', 'debug'),
            port=int(config.get('settings', 'port')))
