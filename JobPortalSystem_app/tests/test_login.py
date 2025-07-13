import unittest
from dao import check_user

class TestAuth(unittest.TestCase):
    def test_correct_credentials(self):
        self.assertTrue(check_user(username="admin", password="123"))

    def test_wrong_username(self):
        self.assertFalse(check_user(username="wrong", password="123"))

    def test_wrong_password(self):
        self.assertFalse(check_user(username="admin", password="wrong"))
