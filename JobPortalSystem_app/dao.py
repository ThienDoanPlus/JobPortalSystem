import json


# Hàm Flask-Login sẽ dùng nó để lấy thông tin user
# từ session mỗi khi bạn tải lại trang.
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