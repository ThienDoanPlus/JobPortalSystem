import os

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest
from .models import User, Resume
from . import dao
from . import db

candidate_bp = Blueprint('candidate', __name__)
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024 # 10 MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@candidate_bp.route('/profile')
@login_required
def profile():
    candidate_profile = dao.get_candidate_profile_by_user_id(current_user.id)

    # Nếu chưa đăng nhập, Flask-Login sẽ tự động chuyển họ về trang login.
    return render_template('profile.html', user=current_user, profile=candidate_profile)


@candidate_bp.route('/cv/create', methods=['GET', 'POST'])
@login_required
def create_cv():
    """Chỉ hiển thị trang chọn mẫu CV."""
    cv_templates = Resume.query.filter_by(is_template=True).order_by(Resume.id).all()
    return render_template('cv_create.html', cv_templates=cv_templates)

@candidate_bp.route('/cv/create-from-template/<int:template_id>', methods=['POST'])
@login_required
def create_cv_from_template(template_id):
    """Xử lý việc tạo CV mới khi người dùng chọn một mẫu."""
    candidate_profile = dao.get_candidate_profile_by_user_id(current_user.id)
    if not candidate_profile:
        flash("Không tìm thấy hồ sơ ứng viên.", "danger")
        return redirect(url_for('candidate.profile'))

    # Gọi hàm DAO đã được hoàn thiện
    new_cv = dao.clone_cv_from_template(
        template_id=template_id,
        candidate_id=candidate_profile.id
    )

    if new_cv:
        flash('Tạo CV mới thành công! Bắt đầu chỉnh sửa ngay.', 'success')
        # Chuyển hướng thẳng đến trang CV Builder
        return redirect(url_for('candidate.edit_cv', cv_id=new_cv.id))
    else:
        flash('Lỗi khi tạo CV. Mẫu không hợp lệ hoặc có lỗi xảy ra.', 'danger')
        return redirect(url_for('candidate.create_cv'))


@candidate_bp.route('/cv/upload', methods=['POST'])
@login_required
def upload_cv():
    """Route này chỉ chuyên xử lý việc upload file CV có sẵn."""
    if request.method == 'POST':
        title = request.form.get('title')
        cv_file = request.files.get('cv_file')

        if not title or not cv_file or cv_file.filename == '':
            flash('Vui lòng nhập tiêu đề và chọn file CV.', 'danger')
            return redirect(url_for('candidate.create_cv'))

        # Lấy lại logic xử lý file từ hàm create_cv cũ
        if not allowed_file(cv_file.filename):
            flash('Chỉ chấp nhận file PDF.', 'danger')
            return redirect(url_for('candidate.create_cv'))

        if cv_file.content_length > MAX_FILE_SIZE:
            flash('Kích thước file không được vượt quá 10MB.', 'danger')
            return redirect(url_for('candidate.create_cv'))

        filename = secure_filename(f"{current_user.id}_{cv_file.filename}")
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        cv_file.save(file_path)
        file_path_for_db = os.path.join('uploads', filename)

        candidate_profile = dao.get_candidate_profile_by_user_id(current_user.id)
        if candidate_profile:
            # Dùng hàm dao cũ để tạo CV chỉ với file
            dao.create_new_cv(candidate_id=candidate_profile.id, title=title, file_path=file_path_for_db)
            flash('Upload CV thành công!', 'success')
            return redirect(url_for('candidate.manage_cvs'))
        else:
            flash('Không tìm thấy hồ sơ ứng viên.', 'danger')

    return redirect(url_for('candidate.create_cv'))

@candidate_bp.route('/cvs')
@login_required
def manage_cvs():
    # Lấy profile và sau đó là các CV liên quan
    candidate_profile = dao.get_candidate_profile_by_user_id(current_user.id)
    cv_list = []
    if candidate_profile:
        cv_list = candidate_profile.resumes.all()

    return render_template('cv_manage.html', cv_list=cv_list)

@candidate_bp.route('/cv/<int:cv_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_cv(cv_id):
    # Lấy CV từ CSDL
    cv = dao.get_cv_by_id(cv_id)

    # Đảm bảo user không thể chỉnh sửa CV của người khác bằng cách thay đổi ID trên URL
    if not cv or cv.candidate.user_id != current_user.id:
        flash('CV không tồn tại hoặc bạn không có quyền chỉnh sửa.', 'danger')
        return redirect(url_for('candidate.manage_cvs'))

    # XỬ LÝ KHI NGƯỜI DÙNG SUBMIT FORM THÊM KINH NGHIỆM
    if request.method == 'POST':
        # Lấy giá trị của nút submit được nhấn
        action = request.form.get('action')

        if action == 'add_experience':
            job_title = request.form.get('job_title')
            company_name = request.form.get('company_name')
            description = request.form.get('description')
            if not job_title or not company_name:
                flash('Chức danh và Tên công ty là bắt buộc.', 'danger')
            else:
                dao.add_experience_to_cv(cv_id=cv.id, job_title=job_title,
                                         company_name=company_name, description=description)
                flash('Thêm kinh nghiệm thành công!', 'success')
            return redirect(url_for('candidate.edit_cv', cv_id=cv.id))

        elif action == 'add_education':
            institution_name = request.form.get('institution_name')
            degree = request.form.get('degree')
            major = request.form.get('major')
            if not institution_name or not degree:
                flash('Tên trường và Bằng cấp là bắt buộc.', 'danger')
            else:
                dao.add_education_to_cv(cv_id=cv.id, institution_name=institution_name,
                                        degree=degree, major=major)
                flash('Thêm học vấn thành công!', 'success')
            return redirect(url_for('candidate.edit_cv', cv_id=cv.id))

        # Lấy danh sách để hiển thị
    experiences = cv.experiences
    educations = cv.educations  # <-- LẤY THÊM DANH SÁCH HỌC VẤN

    return render_template('cv_edit.html', cv=cv, experiences=experiences, educations=educations)

@candidate_bp.route('/cv/<int:cv_id>/preview')
@login_required
def preview_cv(cv_id):
    # Lấy CV từ CSDL
    cv = dao.get_cv_by_id(cv_id)

    # Kiểm tra đảm bảo user chỉ xem được CV của mình
    if not cv or cv.candidate.user_id != current_user.id:
        flash('CV không tồn tại hoặc bạn không có quyền xem.', 'danger')
        return redirect(url_for('candidate.manage_cvs'))

    return render_template('cv_preview.html', cv=cv)


@candidate_bp.route('/cv/<int:cv_id>/delete', methods=['POST'])
@login_required
def delete_cv(cv_id):
    # Lấy CV từ CSDL
    cv = dao.get_cv_by_id(cv_id)

    # Kiểm tra đảm bảo user chỉ xóa được CV của mình
    if not cv or cv.candidate.user_id != current_user.id:
        flash('CV không tồn tại hoặc bạn không có quyền xóa.', 'danger')
        return redirect(url_for('candidate.manage_cvs'))

    # Gọi hàm DAO để xóa
    if dao.delete_cv_by_id(cv_id):
        flash(f'Đã xóa thành công hồ sơ "{cv.title}".', 'success')
    else:
        flash('Đã có lỗi xảy ra khi xóa hồ sơ.', 'danger')

    return redirect(url_for('candidate.manage_cvs'))


@candidate_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user = current_user
    profile = getattr(user, 'candidate_profile', None)

    if request.method == 'POST':
        # Lấy dữ liệu từ form
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        username = request.form.get('username')

        # Cập nhật bảng user
        if email and email != user.email:
            if User.query.filter_by(email=email).first():
                flash('Email đã được sử dụng.', 'danger')
                return redirect(url_for('candidate.settings'))
            user.email = email
        if username and username != user.username:
            if User.query.filter_by(username=username).first():
                flash('Tên đăng nhập đã được sử dụng.', 'danger')
                return redirect(url_for('candidate.settings'))
            user.username = username

        # Cập nhật bảng candidate_profile
        if profile:
            if full_name is not None:
                profile.full_name = full_name
            # Cập nhật luôn cả khi phone là rỗng (cho phép xóa số điện thoại)
            if phone is not None:
                profile.phone_number = phone

        address = request.form.get('address')
        if address is not None:
            profile.address = address

        linkedin_url = request.form.get('linkedin_url')
        if linkedin_url is not None:
            profile.linkedin_url = linkedin_url

        # Đổi mật khẩu nếu có
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if current_password and new_password and confirm_password:
            if not user.check_password(current_password):
                flash('Mật khẩu hiện tại không đúng.', 'danger')
            elif new_password != confirm_password:
                flash('Mật khẩu mới không khớp.', 'danger')
            else:
                user.set_password(new_password)
                flash('Đổi mật khẩu thành công!', 'success')
        try:
            db.session.commit()
            flash('Cập nhật thông tin thành công!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra khi lưu dữ liệu.', 'danger')

        return redirect(url_for('candidate.settings'))

    return render_template('settings.html', user=user, profile=profile)       