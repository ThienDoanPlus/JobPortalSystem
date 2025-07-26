import json
from .models import User, CandidateProfile, Company, RoleEnum, Resume, Experience, Education, JobPost,  db, Application, JobPost, CandidateProfile, Resume, ApplicationStatusEnum
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager
import os
from werkzeug.utils import secure_filename
from flask import current_app
from sqlalchemy.exc import IntegrityError
from .utils import send_application_emails

# Hàm Flask-Login sẽ dùng nó để lấy thông tin user
# từ session mỗi khi bạn tải lại trang.
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

"""
    Tạo một user mới cùng với profile tương ứng.
    Mật khẩu sẽ được hash trước khi lưu.
    """
def create_user(username, email, password, role, full_name=None, company_name=None):
    # Hash mật khẩu để bảo mật
    hashed_password = generate_password_hash(password)

    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        role=role
    )
    db.session.add(new_user)

    # Phải commit để new_user có ID trước khi tạo profile
    db.session.commit()

    # Tạo profile tương ứng với vai trò
    if role == RoleEnum.CANDIDATE and full_name:
        new_candidate = CandidateProfile(user_id=new_user.id, full_name=full_name)
        db.session.add(new_candidate)
    elif role == RoleEnum.RECRUITER and company_name:
        new_company = Company(user_id=new_user.id, name=company_name)
        db.session.add(new_company)

    # Commit lần nữa để lưu profile
    db.session.commit()
    return new_user


def get_user_by_username(username):
    """Tìm user theo username."""
    return User.query.filter_by(username=username).first()

"""Kiểm tra mật khẩu người dùng nhập có khớp với hash trong CSDL không."""
def check_password(user, password):
    if user:
        return check_password_hash(user.password_hash, password)
    return False

"""Lấy CandidateProfile dựa trên user_id."""
def get_candidate_profile_by_user_id(user_id):
    # .first() sẽ trả về đối tượng profile hoặc None nếu không tìm thấy
    return CandidateProfile.query.filter_by(user_id=user_id).first()

"""Tạo một CV mới trong CSDL."""
def create_new_cv(candidate_id, title, file_path=None):
    new_cv = Resume(candidate_id=candidate_id, title=title, cv_file_path=file_path)
    db.session.add(new_cv)
    db.session.commit()
    return new_cv

"""Lấy một CV cụ thể bằng ID của nó."""
def get_cv_by_id(cv_id):
    return Resume.query.get(cv_id)

"""Tạo một bản ghi Experience mới và liên kết nó với một CV."""
def add_experience_to_cv(cv_id, job_title, company_name, description):
    new_experience = Experience(
        resume_id=cv_id,
        job_title=job_title,
        company_name=company_name,
        description=description
        # Tạm thời bỏ qua ngày tháng để đơn giản hóa
    )
    db.session.add(new_experience)
    db.session.commit()
    return new_experience

"""Tạo một bản ghi Education mới và liên kết nó với một CV."""
def add_education_to_cv(cv_id, institution_name, degree, major):
    new_education = Education(
        resume_id=cv_id,
        institution_name=institution_name,
        degree=degree,
        major=major
    )
    db.session.add(new_education)
    db.session.commit()
    return new_education

"""Lấy Company profile dựa trên user_id."""
def get_company_by_user_id(user_id):
    return Company.query.filter_by(user_id=user_id).first()

"""Tạo một JobPost mới trong CSDL."""
def create_job_post(company_id, data):
    salary_min = data.get('salary_min') or None
    salary_max = data.get('salary_max') or None

    new_job = JobPost(
        company_id=company_id,
        title=data.get('title'),
        description=data.get('description'),
        requirements=data.get('requirements'),
        benefits=data.get('benefits'),
        location=data.get('location'),
        salary_min=salary_min,
        salary_max=salary_max,
        job_type=data.get('job_type'),
        experience_level=data.get('experience_level')
    )
    db.session.add(new_job)
    db.session.commit()
    return new_job

"""Tìm và xóa một CV khỏi CSDL."""
def delete_cv_by_id(cv_id):
    cv = Resume.query.get(cv_id)
    if cv:
        db.session.delete(cv)
        db.session.commit()
        return True
    return False

"""Lấy danh sách công việc mới nhất"""
def get_latest_jobs(limit=10):
    return JobPost.query.filter_by(active=True) \
        .order_by(JobPost.created_date.desc()) \
        .limit(limit).all()

"""Lấy công việc theo bộ lọc"""
def get_jobs_by_filters(location=None, job_type=None, experience_level=None, limit=20):
    query = JobPost.query.filter_by(active=True)

    if location:
        query = query.filter(JobPost.location.contains(location))
    if job_type:
        query = query.filter_by(job_type=job_type)
    if experience_level:
        query = query.filter_by(experience_level=experience_level)

    return query.order_by(JobPost.created_date.desc()).limit(limit).all()

"""Lấy thông tin chi tiết công việc"""
def get_job_by_id(job_id):

    return JobPost.query.get(job_id)


"xử lý nộp CV"


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_application(job_id, candidate_id, resume_id=None, cv_file=None):
    """
    Tạo một đơn ứng tuyển mới.
    - Kiểm tra xem ứng viên đã ứng tuyển công việc này chưa.
    - Xử lý việc ứng tuyển bằng CV online (resume_id) hoặc file tải lên (cv_file).
    """
    # 1. Kiểm tra xem ứng viên đã ứng tuyển vào công việc này chưa
    existing_application = Application.query.filter_by(
        candidate_id=candidate_id,
        job_id=job_id
    ).first()
    if existing_application:
        raise ValueError("Bạn đã ứng tuyển vào công việc này rồi.")

    # 2. Tạo đối tượng Application mới
    new_application = Application(
        job_id=job_id,
        candidate_id=candidate_id,
        status=ApplicationStatusEnum.RECEIVED
    )

    cv_file_path = None  # Biến để lưu đường dẫn file nếu có

    # 3. Xử lý file tải lên nếu có
    if cv_file and cv_file.filename != '':
        # 3.1. Kiểm tra file
        if not allowed_file(cv_file.filename):
            raise ValueError('Định dạng file không hợp lệ. Chỉ chấp nhận file PDF.')

        # Sử dụng content_length để kiểm tra kích thước file một cách an toàn
        if cv_file.content_length > MAX_FILE_SIZE:
            raise ValueError('Kích thước file không được vượt quá 10MB.')

        # 3.2. Lưu file
        filename = secure_filename(f"application_{candidate_id}_{job_id}_{cv_file.filename}")
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')  # Lấy từ config
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        cv_file_path = os.path.join(upload_folder, filename)
        cv_file.save(cv_file_path)

        # Lưu đường dẫn tương đối để truy cập từ web
        new_application.cv_file_url = os.path.join('uploads', filename)

    # 4. Xử lý CV online nếu có
    elif resume_id:
        # Kiểm tra xem resume_id có hợp lệ và thuộc về ứng viên không
        resume = Resume.query.filter_by(id=resume_id, candidate_id=candidate_id).first()
        if not resume:
            raise ValueError("CV online không hợp lệ hoặc không thuộc về bạn.")
        new_application.resume_id = resume_id

    else:
        # Trường hợp không có cả hai
        raise ValueError("Cần phải cung cấp CV online hoặc tải lên file CV.")

    # 5. Lưu vào CSDL
    try:
        db.session.add(new_application)
        db.session.commit()

        # Sau khi commit thành công, chúng ta có new_application.id
        # Bây giờ, chúng ta sẽ cố gắng gửi email
        try:
            # Gọi hàm gửi mail với ID của đơn ứng tuyển vừa tạo
            send_application_emails(new_application.id)
        except Exception as e:
            # Nếu gửi mail lỗi, chỉ ghi log lại chứ không làm hỏng request chính
            # Người dùng vẫn nhận được thông báo ứng tuyển thành công trên web
            current_app.logger.error(f"Không thể gửi email xác nhận cho application ID {new_application.id}: {e}")

        # Trả về đối tượng application đã được lưu thành công
        return new_application

    except IntegrityError as e:
        db.session.rollback()
        # Lỗi này thường xảy ra do race condition hoặc người dùng đã ứng tuyển rồi
        current_app.logger.warning(f"IntegrityError khi tạo application: {e}")
        raise ValueError("Bạn đã ứng tuyển vào công việc này rồi.")

    except Exception as e:
        db.session.rollback()
        # Xóa file đã tải lên nếu có lỗi xảy ra với CSDL
        if 'cv_file_path' in locals() and cv_file_path and os.path.exists(cv_file_path):
            os.remove(cv_file_path)
        current_app.logger.error(f"Lỗi không xác định khi tạo application: {e}")
        raise e




