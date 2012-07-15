python-filebutler
========================

filebutler is a small web app based on flask that allows you to upload(post) files over http/https and get a sha1 link in return.
filebutler uses sqlite as backend to keep track of files.

I suggest that you use python-filebutler together with [filebutler-upload](http://github.com/jhaals/filebutler-upload "filebutler-upload") or write your own upload app.

Features
---------

###### Authentication
User/Password authentication to upload files.
Passwords are stored hmac encrypted.
###### Password protected files
Ability to password protect your files.
###### One time download
Your file will only be available for one download.
###### Expire date
Ability to set expire date. 1 hour, 1 day, 1 week, 1 month

Usage
------

#### Upload files

Send POST to data to filebutler containing these fields.

    file (mandatory(the file you wish to upload))
    username (mandatory)
    password (mandatory)
    download_password (optional)
    one_time_download (optional or 1)
    expire (optional or 1h, 1d, 1w or 1m)

Headers must be set to __Accept: application/json__ else html will be returned

##### Response format
Filebutler will return a json encoded message and throw http status codes.
A successful upload will return status code 200 and a URL

    { "message": "http://upload.example.com/download?u=f1d2d2f924e986ac86fdf7b36c94bcdf32beec15" }

#### manage.py

Perform management operations such as create/delete users.

available commands:

    --add-user <username>
    --delete-user <username>
    --change-password <username>
    --delete-expired-data

Expired files that's never been downloaded won't get removed automatically.
It's recommended to run --delete-expired-data periodically to clean storage and database from expired files

Installation
-----

Install python requirements using pip

    pip install -r requirements.txt

-   configure ppupload.conf and place it under /etc/filebutler.conf
-   create the directory specified as storage_path in filebutler.conf
-   changed the secret_key in filebutler.conf
-   Create users via manage.py --add-user <username>
-   Run main.py

### Deployment
Simple deployment examples can be found at http://flask.pocoo.org/


