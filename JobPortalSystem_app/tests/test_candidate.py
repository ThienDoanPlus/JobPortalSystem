import io
from JobPortalSystem_app import dao
from JobPortalSystem_app.models import Resume, User


def test_profile_page_access(logged_in_client):
    response = logged_in_client.get('/profile')
    assert response.status_code == 200
    assert b'Test Candidate' in response.data

# def test_manage_cvs_page_empty(logged_in_client):
#     response = logged_in_client.get('/cvs')
#     assert response.status_code == 2000
#     assert 'Bạn chưa tạo CV nào'.encode('utf-8') in response.data

def test_upload_cv_success(logged_in_client, app):
    file_data = (io.BytesIO(b"dummy pdf content"), 'test_cv.pdf')
    data = {
        'title': 'CV Test Upload',
        'cv_file': file_data
    }

    response = logged_in_client.post('/cv/upload', data=data, follow_redirects=True)

    assert response.status_code == 200
    assert 'Upload CV thành công!'.encode('utf-8') in response.data
    assert 'CV Của Tôi'.encode('utf-8') in response.data

    with app.app_context():
        user = User.query.filter_by(username='testcandidate').first()
        candidate_profile = dao.get_candidate_profile_by_user_id(user.id)
        cv = Resume.query.filter_by(candidate_id=candidate_profile.id, title='CV Test Upload').first()
        assert cv is not None
        assert 'uploads' in cv.cv_file_path
        assert '.pdf' in cv.cv_file_path


def test_upload_cv_wrong_file_type(logged_in_client):
    file_data = (io.BytesIO(b"this is a text file"), 'document.txt')
    data = {
        'title': 'CV File Text',
        'cv_file': file_data
    }

    response = logged_in_client.post('/cv/upload', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert 'Chỉ chấp nhận file PDF.'.encode('utf-8') in response.data

def test_delete_cv_success(logged_in_client, app):
    cv_id_to_delete = None
    with app.app_context():
        # Lấy lại user từ DB trong context này để tránh lỗi DetachedInstance
        user = User.query.filter_by(username='testcandidate').first()
        candidate_profile = dao.get_candidate_profile_by_user_id(user.id)

        cv_to_delete = dao.create_new_cv(candidate_id=candidate_profile.id, title='CV Sắp Bị Xóa')
        cv_id_to_delete = cv_to_delete.id

    assert cv_id_to_delete is not None

    response = logged_in_client.post(f'/cv/{cv_id_to_delete}/delete', follow_redirects=True)

    assert response.status_code == 200
    assert 'Đã xóa thành công hồ sơ'.encode('utf-8') in response.data

    with app.app_context():
        deleted_cv = dao.get_cv_by_id(cv_id_to_delete)
        assert deleted_cv is None