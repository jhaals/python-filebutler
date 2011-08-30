#!/usr/bin/env python
# Copyright (c) 2011, Johan Haals <johan.haals@gmail.com>
# All rights reserved.

import hashlib
import os
import paramiko
import sys
import ConfigParser as configparser
from os.path import join
from datetime import datetime
from dateutil.relativedelta import *
from optparse import OptionParser

config = configparser.RawConfigParser()
if not config.read([os.path.expanduser('~/.ppupload.conf') or 'ppupload.conf', '/etc/ppupload.conf']):
    sys.exit("Couldn't read configuration file")

#config.get('remote', 'username')
usage = 'usage: %prog -h'
parser = OptionParser(usage, version="%prog 0.1")
parser.add_option("--file", "-f", help='Specify file to upload')
parser.add_option("--onetime", "-1", help='One time download(optional)', default=False, action='store_true')
parser.add_option("--lifetime", "-l", help='Lifetime(optional): 1h, 1d, 1w, 1m (hour/day/week/month). Default lifetime is unlimited')
parser.add_option("--password", "-p", help='Download password(optional)')

(options, args) = parser.parse_args()

if not options.file:
    parser.error('Specify --file')
elif not os.path.isfile(options.file):
    sys.exit('File does not exist')
else:
    filename = os.path.basename(options.file)

if options.onetime:
    one_time_download = 1
else:
    one_time_download = 0

if options.password:
    password = hashlib.new('md5')
    password.update(options.password)
    password = password.hexdigest()
else:
    password = ''

if options.lifetime:
    if options.lifetime == '1h':
        lifetime = datetime.now() + relativedelta(hours=1)
        expire = lifetime.strftime('%Y%m%d%H%M')
    elif options.lifetime == '1d':
        lifetime = datetime.now() + relativedelta(days=1)
        expire = lifetime.strftime('%Y%m%d%H%M')
    elif options.lifetime == '1w':
        lifetime = datetime.now() + relativedelta(weeks=1)
        expire = lifetime.strftime('%Y%m%d%H%M')
    elif options.lifetime == '1m':
        lifetime = datetime.now() + relativedelta(weeks=4)
        expire = lifetime.strftime('%Y%m%d%H%M')
    else:
        parser.error('Unknown lifetime')
else:
    expire = ''

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Use private key to authenticate to server
try:
    privkey = paramiko.RSAKey.from_private_key_file (config.get('local', 'private_rsa_key'))
except IOError:
    sys.exit('Could not open private key, check location')
except paramiko.PasswordRequiredException:
    sys.exit('Private key file is encrypted')

# Connecting!
try:
    ssh.connect(config.get('remote', 'hostname'), username=config.get('remote', 'username'),pkey=privkey, timeout=10)
except paramiko.AuthenticationException:
    sys.exit('Authentication failed. Check username/private key')
except SSHException as error:
    sys.exit(error)
except socket.error as error:
    sys.exit(error)
 
#Transfering files to and from the remote machine
sftp = ssh.open_sftp()
try:
    sftp.put(options.file, join(config.get('remote', 'storage_path'), filename))
except IOError as error:
    sys.exit('Permission denied, check permissions. Error msg: %s' % error)
except OSError as error:
    sys.exit(error)

# Generate download hash (should be rewritten) 
microtime = datetime.now().strftime('%f')
download_hash = hashlib.new('md5')
download_hash.update(microtime+filename)
download_hash = download_hash.hexdigest()

# Write database file on remote host
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('echo "%s:%s:%s:%s" >> %s%s' % (filename, password, expire, one_time_download, config.get('remote', 'database_path'), download_hash))
error = ssh_stderr.read()

#Reading the error stream of the executed command
if len(error) != 0:
    sys.exit('Error: %s' % error)
else:
# everything should be fine, print download url
    download_url = config.get('remote', 'url')+download_hash
    if sys.platform == 'darwin':
        os.system('echo %s | pbcopy' % download_url)
    print download_url

# Close connections
sftp.close()
ssh.close()
