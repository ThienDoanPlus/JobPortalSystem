# tests/test_login.py
import unittest
from dao import check_user

class TestLogin(unittest.TestCase):
    def test_correct_credentials(self):
        self.assertTrue(check_user("admin", "123"))

    def test_wrong_password(self):
        self.assertFalse(check_user("admin", "wrongpass"))

    def test_nonexistent_user(self):
        self.assertFalse(check_user("notexist", "123"))

if __name__ == '__main__':
    unittest.main()
