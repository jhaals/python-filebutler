from filebutler.fbquery import FbQuery
from datetime import datetime
import unittest


class PasswordTests(unittest.TestCase):

    def setUp(self):
        self.fb = FbQuery()

    # User tests
    def testUserCreate(self):
        self.assertTrue(self.fb.user_create(
            'testuser',
            'randomPassword'
        ))
        self.fb.user_delete('testuser')

    def testUserExists(self):
        self.fb.user_create('testUser', 'randomPassword')
        self.assertTrue(self.fb.user_exist('testUser'))
        self.fb.user_delete('testUser')

    def testUserExistsInvalid(self):
        self.assertFalse(self.fb.user_exist('invalidUser'))

    def testChangePassword(self):
        self.fb.user_create('testuser', 'randomPassword')
        self.assertTrue(self.fb.user_change_password('testuser', 'somepassword'))
        self.fb.user_delete('testuser')

    def testChangePasswordNonExistingUser(self):
        self.assertFalse(self.fb.user_change_password('jkhkjhkjh', 'somepassword'))

    def testUserDelete(self):
        self.fb.user_create('userDeleteTest', 'randomPassword')
        self.assertTrue(self.fb.user_delete('userDeleteTest'))

    def testUserDeleteNonExisting(self):
        self.assertFalse(self.fb.user_delete('non-existing-user'))

    def testUserGet(self):
        u = 'testuser'
        self.fb.user_create(u, 'randomPassword')
        user = self.fb.user_get(u)
        self.assertEqual(user.username, u)
        self.fb.user_delete(u)

    def testUserGetNonExisting(self):
        self.assertIsNone(self.fb.user_get('unkownUser'))

    def testUserListFiles(self):
        user = 'Testing'
        file_hash = '1337'
        file_name = 'random_file_name'
        self.fb.user_create(user, 'password')
        user_data = self.fb.user_get(user)
        self.fb.file_add(file_hash, user_data.id, file_name, 0, False, False)
        data = self.fb.user_list_files(user)
        self.assertEqual(data['message'][file_hash]['filename'], file_name)
        self.fb.file_remove(file_hash, file_name)
        self.fb.user_delete(user)

    def testUserNonExistingListFiles(self):
        self.assertIsNone(self.fb.user_list_files('invalid-user'))

    # File tests

    def testFileAdd(self):
        self.assertTrue(self.fb.file_add('123', 1, 'testfile', 0, False, False))

    def testFileGetNoneExisting(self):
        self.assertIsNone(self.fb.file_get('unkown_hash'))

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

    def testFileExpiredValueError(self):
        invalid_date = 'abc'
        self.assertRaises(self.fb.file_expired(invalid_date))

    def testNonExpiredFile(self):
        date_in_the_future = '20700101010101'
        self.assertFalse(self.fb.file_expired(date_in_the_future))

    def testFileRemoveExpired(self):
        expire_date = datetime.now().strftime('%Y%m%d%H%M%S')
        hash = 'SJG8F90G8S09'
        testfile = 'testFileRemoveExpired'
        self.fb.user_create('testuser', 'password')
        self.fb.file_add(hash, 1, testfile, expire_date, False, False)
        self.assertEqual(testfile, self.fb.file_remove_expired()['message'][hash]['filename'])
        self.fb.user_delete('testuser')

if __name__ == "__main__":
    unittest.main()
