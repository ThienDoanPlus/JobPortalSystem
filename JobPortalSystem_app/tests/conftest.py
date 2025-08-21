# --- START OF FILE JobPortalSystem_app/tests/
# test_dao.py (Đã sửa lỗi) ---

import pytest
from JobPortalSystem_app.models import User, RoleEnum

# Test /register
def test_register_get(client):
    """Test trang đăng ký có thể truy cập (GET request)."""
    response = client.get('/register')
    assert response.status_code == 200
    # Sửa lại cho khớp với thẻ h2 trong register.html
    assert '<h2>Tạo Tài Khoản Mới</h2>'.encode('utf-8') in response.data

def test_register_candidate_post_success(client, app, test_user_data):
    """Test đăng ký ứng viên thành công."""
    with app.app_context():
        response = client.post('/register', data={
            'username': test_user_data['username'],
            'email': test_user_data['email'],
            'password': test_user_data['password'],
            'role': RoleEnum.CANDIDATE.value,
            'full_name': test_user_data['full_name']
        }, follow_redirects=True)

        assert response.status_code == 200
        # Sửa lại cho khớp với flash message trong auth.py
        assert 'Đăng ký thành công! Vui lòng đăng nhập.'.encode('utf-8') in response.data
        # Kiểm tra đã chuyển đến trang login thành công
        assert '<h2>Đăng Nhập</h2>'.encode('utf-8') in response.data

        user = User.query.filter_by(username=test_user_data['username']).first()
        assert user is not None
        assert user.role == RoleEnum.CANDIDATE
        assert user.candidate_profile.full_name == test_user_data['full_name']

def test_register_duplicate_username(client, create_test_user, test_user_data):
    """Test đăng ký với username đã tồn tại."""
    create_test_user(test_user_data['username'], test_user_data['email'],
                     test_user_data['password'], RoleEnum.CANDIDATE,
                     full_name=test_user_data['full_name'])

    response = client.post('/register', data={
        'username': test_user_data['username'],
        'email': 'another@example.com',
        'password': 'newpassword',
        'role': RoleEnum.CANDIDATE.value,
        'full_name': 'Another Candidate'
    })
    assert response.status_code == 200
    # Sửa lại cho khớp với flash message trong auth.py
    assert 'Tên đăng nhập đã tồn tại.'.encode('utf-8') in response.data

# Test /login
def test_login_get(client):
    """Test trang đăng nhập có thể truy cập (GET request)."""
    response = client.get('/login')
    assert response.status_code == 200
    # Sửa lại cho khớp với thẻ h2 trong login.html
    assert '<h2>Đăng Nhập</h2>'.encode('utf-8') in response.data

def test_login_success(client, create_test_user, test_user_data):
    """Test đăng nhập thành công."""
    user = create_test_user(test_user_data['username'], test_user_data['email'],
                            test_user_data['password'], RoleEnum.CANDIDATE,
                            full_name=test_user_data['full_name'])

    response = client.post('/login', data={
        'username': test_user_data['username'],
        'password': test_user_data['password']
    }, follow_redirects=True)

    assert response.status_code == 200
    # Sửa lại cho khớp với flash message trong auth.py
    assert 'Đăng nhập thành công!'.encode('utf-8') in response.data
    # Kiểm tra nội dung của trang chủ (trang được chuyển hướng đến)
    assert 'Việc Làm'.encode('utf-8') in response.data

    with client.session_transaction() as sess:
        assert '_user_id' in sess
        assert sess['_user_id'] == str(user.id)

def test_login_invalid_password(client, create_test_user, test_user_data):
    """Test đăng nhập với mật khẩu sai."""
    create_test_user(test_user_data['username'], test_user_data['email'],
                     test_user_data['password'], RoleEnum.CANDIDATE,
                     full_name=test_user_data['full_name'])

    response = client.post('/login', data={
        'username': test_user_data['username'],
        'password': 'wrongpassword'
    })
    assert response.status_code == 200
    # Sửa lại cho khớp với flash message trong auth.py
    assert 'Tên đăng nhập hoặc mật khẩu không đúng.'.encode('utf-8') in response.data

# Test /logout
def test_logout(client, create_test_user, test_user_data):
    """Test đăng xuất."""
    # Đăng nhập user trước
    create_test_user(test_user_data['username'], test_user_data['email'],
                     test_user_data['password'], RoleEnum.CANDIDATE,
                     full_name=test_user_data['full_name'])
    client.post('/login', data={
        'username': test_user_data['username'],
        'password': test_user_data['password']
    })

    # Đăng xuất
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    # Kiểm tra đã về trang login
    assert '<h2>Đăng Nhập</h2>'.encode('utf-8') in response.data

    with client.session_transaction() as sess:
        assert '_user_id' not in sess