import unittest
from dao import *

class TestAuth(unittest.TestCase):
    def test_correct_credentials(self):
        """Test đăng nhập đúng"""
        self.assertTrue(check_user(username="admin", password="123"))

    def test_wrong_password(self):
        """Test sai mật khẩu"""
        self.assertFalse(check_user(username="admin", password="wrongpass"))

    def test_nonexistent_user(self):
        """Test người dùng không tồn tại"""
        self.assertFalse(check_user(username="notexist", password="123"))

if __name__ == '__main__':
    unittest.main()