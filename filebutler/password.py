#!/usr/bin/env python
# Copyright (c) 2011-2012, Johan Haals <johan.haals@gmail.com>
# All rights reserved.

import hmac
import hashlib

class Password:

    # TODO
    #   Support for multiple hash algorithms

    def __init__(self, secret_key):
        self.secret_key = secret_key

    def random(self, chars):
        ''' returns a random hex string based on the output of /dev/urandom '''
        f = open('/dev/urandom', 'rb')

        return f.read(chars).encode('hex')

    def generate(self, password):
        ''' Encrypt password using our secure_key and a random salt from random(). return sha1:hmachash:salt '''
        salt = self.random(225)
        hmac_hash = hmac.new(self.secret_key,password + salt, hashlib.sha1).hexdigest()

        return 'sha1:%s:%s' % (hmac_hash, salt)

    def validate(self, hash, password):
        ''' split hash and extract it's salt. Create new hash for password using salt and our secret_key. If both hashes match return true '''
        try:
            algorithm, hash, salt = hash.split(':')
        except ValueError:
            # Invalid password hash. Should be sha1:hmac_hash:salt
            raise ValueError('Invalid password string syntax')

        # encrypt password with extracted salt from hash
        self.password_hash = hmac.new(self.secret_key, password + salt, hashlib.sha1).hexdigest()

        if self.password_hash != hash:
            return False

        # password is valid
        return True
