from filebutler.fbquery import FbQuery
import unittest


class PasswordTests(unittest.TestCase):

    def setUp(self):
        self.username = 'testUser'
        self.fb = FbQuery()

    # User tests
    def testUserCreate(self):
        self.assertTrue(self.fb.user_create(
            self.username,
            'randomPassword'
        ))

    def testUserExists(self):
        self.assertTrue(self.fb.user_exist('testUser'))

    def testUserExistsInvalid(self):
        self.assertFalse(self.fb.user_exist('invalidUser'))

    def testChangePassword(self):
        self.assertTrue(self.fb.user_change_password(self.username, 'somepassword'))

    def testUserDelete(self):
        self.assertTrue(self.fb.user_create(
            'userDeleteTest',
            'randomPassword'
        ))
        self.assertTrue(self.fb.user_delete('userDeleteTest'))

    def testUserGet(self):
        user = self.fb.user_get(self.username)
        self.assertEqual(user.username, self.username)

    def testUserListFiles(self):
        user = 'Testing'
        file_hash = '1337'
        file_name = 'random_file_name'
        self.fb.user_create(user, 'password')
        user_data = self.fb.user_get(user)
        self.fb.file_add(file_hash, user_data.id, file_name, 0, False, False)
        data = self.fb.user_list_files(user)
        self.assertEqual(data['message'][file_hash]['filename'], file_name)
    # File tests

    def testFileAdd(self):
        self.assertTrue(self.fb.file_add('123', 1, 'testfile', 0, False, False))

    def testSetFileExpiry(self):
        test_date = '2000-01-01 00:00:00'
        hash = '8765'
        self.fb.file_add(hash, 1, 'testfile', 0, False, False)
        self.fb.file_set_expiry(hash, test_date)
        f = self.fb.file_get(hash)
        self.assertEqual(f.expire, test_date)
        self.fb.file_remove(hash, 'testfile')

    def testFileDelete(self):
        self.assertTrue(self.fb.file_remove('123', 'testfile'))

    def testFileDeleteUnknownFile(self):
        self.assertFalse(self.fb.file_remove('9999', 'unknownFile'))

    def testExpiredFile(self):
        date_from_the_past = '20110101010101'
        self.assertTrue(self.fb.file_expired(date_from_the_past))

    def testNonExpiredFile(self):
        date_in_the_future = '20700101010101'
        self.assertFalse(self.fb.file_expired(date_in_the_future))

    def testFileRemoveExpired(self):
        expire_date = '2000-01-01 00:00:00'
        hash = '8765'
        self.fb.file_add(hash, 1, 'testfile', expire_date, False, False)
        #TODO: Fixthis!!
        self.fb.file_remove(hash, 'testfile')

if __name__ == "__main__":
    unittest.main()
