import sys
import pytest
from unittest.mock import MagicMock

# 1. Mock weasyprint ngay từ đầu để tránh lỗi OSError
MOCK_WEASYPRINT = MagicMock()
sys.modules['weasyprint'] = MOCK_WEASYPRINT
sys.modules['weasyprint.HTML'] = MagicMock()

# 2. Bây giờ mới import các thành phần của app
from JobPortalSystem_app import create_app, db, dao
from JobPortalSystem_app.models import User, RoleEnum, CandidateProfile

@pytest.fixture(scope='function')
def app():
    """
    Fixture tạo ra một instance Flask app cho mỗi test function.
    Đảm bảo mỗi test chạy trên một môi trường sạch.
    """
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Fixture cung cấp một test client cho app."""
    return app.test_client()

@pytest.fixture(scope='function')
def test_user(app):
    """Fixture tạo ra một user CANDIDATE mẫu trong DB và trả về đối tượng User."""
    with app.app_context():
        user = dao.create_user(
            username='testcandidate',
            email='candidate@test.com',
            password='password123',
            role=RoleEnum.CANDIDATE,
            full_name='Test Candidate'
        )
        return user

@pytest.fixture(scope='function')
def logged_in_client(client, test_user):
    """
    Fixture cung cấp một test client ĐÃ ĐĂNG NHẬP SẴN với vai trò CANDIDATE.
    Đây là fixture cực kỳ hữu ích để test các route cần @login_required.
    """
    # Giả lập việc gửi form login
    client.post('/login', data={
        'username': 'testcandidate',
        'password': 'password123'
    }, follow_redirects=True)

    yield client

    # Sau khi test xong, logout để dọn dẹp session
    client.get('/logout', follow_redirects=True)