#!/usr/bin/env python
# Copyright (c) 2011-2012, Johan Haals <johan.haals@gmail.com>
# All rights reserved.

# Standard library
import getpass
import os
import sys
from argparse import ArgumentParser
from ConfigParser import RawConfigParser


def ask(question, yes_no=False):
    while 1:
        if yes_no:
            answer = raw_input(question + '[y/n]: ')
            if answer == 'y':
                return True
            elif answer == 'n':
                return False
            else:
                continue
            break
        if not yes_no:
            answer = raw_input(question + ': ')
        if not len(answer):
            continue
        break
    return answer


def configuration_tutorial():
    print "python-filebutler couldn't detect the configuration file."
    print
    print 'Specify address to the webserver where filebutler should run'
    print 'The URL will be used to assemble download links'
    print "If you want to test locally use: http://127.0.0.1:5000"
    url = ask('url')
    try:
        port = url.split(':')[2]
    except IndexError:
        sys.exit('Could not detect port in URL')

    debug = ask('Enable debug mode', yes_no=True)
    if debug:
        debug = 'True'
    else:
        debug = 'False'

    storage_path = ask('Storage directory, where files will be stored')
    if not os.path.isdir(storage_path):
        sys.exit('%s is not a valid storage path' % storage_path)

    database_path = ask(
        'Database path, where sqlite database should be located')

    if not os.path.isdir(database_path):
        sys.exit(
            '%s is not a valid directory for the database' % database_path)
    database_path = os.path.join(database_path, 'filebutler.sqlite')

    print 'Enter a secret key (will be used to encrypt passwords)'
    print 'Type at least 100 random characters.'
    secret_key = ask('Secret Key')
    print
    print 'Storage path:', storage_path
    print 'Database path:', database_path
    print 'Debug:', debug
    print 'URL:', url

    if ask('Is this information correct?', yes_no=True):
        config_path = 'python-filebutler.conf'
        print 'Writing config file to %s' % config_path

        with open(config_path, 'w') as f:
            f.write('''[settings]
url = {url}
debug = {debug}
port = {port}
storage_path = {storage_path}
database_path = {database_path}
secret_key = {secret_key}
'''.format(
    url=url,
    debug=debug,
    port=port,
    storage_path=storage_path,
    database_path=database_path,
    secret_key=secret_key))
    else:
        # restart tutorial...
        configuration_tutorial()

paths = [
    'python-filebutler.conf',
    '/etc/python-filebutler.conf',
]

config = RawConfigParser()
if not config.read(paths):
    configuration_tutorial()

from fbquery import FbQuery


def user_add(options):
    if options.password:
        password = options.password
    else:
        password = getpass.getpass('Password:')

    if fb.user_exist(options.username):
        print 'User %s already exists!' % options.username
    else:
        if fb.user_create(options.username, password):
            print 'Created user %s' % options.username
        else:
            print 'failed to create user %s' % options.username

def user_delete(options):
    if options.username:
        if fb.user_delete(options.username):
            print 'User %s deleted' % options.username
        else:
            print 'Could not delete %s' % options.username

def user_change_password(options):
    if options.password:
        password = options.password
    else:
        password = getpass.getpass('Password:')

    if fb.user_change_password(options.username, password):
        print 'Password changed'
    else:
        print 'Password change failed'

def delete_expired_data(options):
    for hash, file in fb.file_remove_expired()['message'].iteritems():
        print hash, file['filename'], file['owner']

def parse_arguments():
    parser = ArgumentParser(usage='%(prog)s -h')
    subparsers = parser.add_subparsers()

    parser_user_add = subparsers.add_parser('user-add')
    parser_user_add.set_defaults(command=user_add)
    parser_user_add.add_argument('username',
        metavar='<username>', help='Username for new user')
    parser_user_add.add_argument('-p', '--password',
        metavar='<password>', help='password for new user')

    parser_user_delete = subparsers.add_parser('user-delete')
    parser_user_delete.set_defaults(command=user_delete)
    parser_user_delete.add_argument('username',
        metavar='<username>', help='Username to delete')

    parser_user_change_password = subparsers.add_parser('user-change-password')
    parser_user_change_password.set_defaults(command=user_change_password)
    parser_user_change_password.add_argument('username',
        metavar='<username>', help='User to change password for')
    parser_user_change_password.add_argument('-p', '--password',
        metavar='<password>', help='New password for user')

    parser_delete_expired_data = subparsers.add_parser('delete-expired-data')
    parser_delete_expired_data.set_defaults(command=delete_expired_data)

    return parser.parse_args()


if __name__ == "__main__":
    fb = FbQuery()
    options = parse_arguments()
    if hasattr(options, 'command'):
        options.command(options)
