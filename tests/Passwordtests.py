from filebutler.password import Password
import unittest

class PasswordTests(unittest.TestCase):
    def setUp(self):
        self.secret = 'mysecret'
        self.pw = Password(self.secret)

    def testValidPassword(self):
        self.assertTrue(self.pw.validate(self.pw.generate('password'), 'password'))

    def testInvalidPassword(self):
        self.assertFalse(self.pw.validate(self.pw.generate('password'), 'invalid_password'))

    def testInvalidHash(self):
        with self.assertRaises(ValueError):
            self.pw.validate('invalid_password_hash', 'password_to_verify')

    def testGenerate(self):
        self.assertEqual(len(self.pw.generate('password')), 496)

    def testRandom(self):
        self.assertEqual(len(self.pw.random(128)), 256)

if __name__ == "__main__":
    unittest.main()
