# --- START OF FILE JobPortalSystem_app/tests/test_dao.py (Phiên bản Unit Test thực sự) ---

import unittest
from flask import Flask
from JobPortalSystem_app import db, dao
from JobPortalSystem_app.config import TestingConfig
from JobPortalSystem_app.models import User, RoleEnum, CandidateProfile

class DAOTestCase(unittest.TestCase):

    def setUp(self):
        """
        Thiết lập một môi trường Flask tối giản, CHỈ ĐỦ để test database.
        Chúng ta không gọi create_app() để tránh import các blueprint không cần thiết.
        """
        # 1. Tạo một instance Flask thủ công
        self.app = Flask(__name__)
        # 2. Nạp cấu hình testing (quan trọng nhất là chuỗi kết nối DB)
        self.app.config.from_object(TestingConfig)

        # 3. Gắn SQLAlchemy vào app tối giản này
        db.init_app(self.app)

        # 4. Push app context để có thể thao tác với db.session
        self.app_context = self.app.app_context()
        self.app_context.push()

        # 5. Tạo tất cả các bảng
        db.create_all()

        # --- Tạo dữ liệu mẫu (giữ nguyên như cũ) ---
        self.test_username = 'testuser'
        self.test_password_plain = 'password123'
        self.test_email = 'test@example.com'

        test_user = User(
            username=self.test_username,
            email=self.test_email,
            role=RoleEnum.CANDIDATE
        )
        test_user.set_password(self.test_password_plain)
        db.session.add(test_user)
        db.session.commit()

        test_profile = CandidateProfile(user_id=test_user.id, full_name="Test User")
        db.session.add(test_profile)
        db.session.commit()

    def tearDown(self):
        """Dọn dẹp môi trường test (giữ nguyên như cũ)."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # --- Các hàm test_* giữ nguyên, chúng sẽ hoạt động đúng trong môi trường mới ---

    def test_get_user_by_username_success(self):
        """Kiểm thử lấy user thành công bằng username."""
        user = dao.get_user_by_username(self.test_username)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, self.test_username)

    def test_get_user_by_username_fail(self):
        """Kiểm thử lấy user không tồn tại."""
        user = dao.get_user_by_username('nonexistentuser')
        self.assertIsNone(user)

    def test_check_password_success(self):
        """Kiểm thử kiểm tra mật khẩu đúng."""
        user = dao.get_user_by_username(self.test_username)
        self.assertIsNotNone(user)
        is_correct = dao.check_password(user, self.test_password_plain)
        self.assertTrue(is_correct)

    def test_check_password_fail(self):
        """Kiểm thử kiểm tra mật khẩu sai."""
        user = dao.get_user_by_username(self.test_username)
        self.assertIsNotNone(user)
        is_correct = dao.check_password(user, 'wrongpassword')
        self.assertFalse(is_correct)

    def test_check_password_with_nonexistent_user(self):
        """Kiểm thử kiểm tra mật khẩu với user là None."""
        is_correct = dao.check_password(None, self.test_password_plain)
        self.assertFalse(is_correct)

if __name__ == '__main__':
    unittest.main()