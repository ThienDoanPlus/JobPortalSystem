import os

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from . import dao

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
    if request.method == 'POST':
        title = request.form.get('title')
        cv_file = request.files.get('cv_file')
        file_path = None

        if not title:
            flash('Vui lòng nhập tiêu đề cho CV.', 'danger')
            return render_template('cv_create.html')

        # Xử lý file nếu có
        if cv_file and cv_file.filename != '':
            if not allowed_file(cv_file.filename):
                flash('Chỉ chấp nhận file PDF.', 'danger')
                return render_template('cv_create.html')

            # Kiểm tra kích thước file
            if cv_file.content_length > MAX_FILE_SIZE:
                flash('Kích thước file không được vượt quá 10MB.', 'danger')
                return render_template('cv_create.html')

            filename = secure_filename(cv_file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            cv_file.save(file_path)
            # Lưu đường dẫn tương đối để dùng trong template
            file_path = os.path.join('uploads', filename)

        candidate_profile = dao.get_candidate_profile_by_user_id(current_user.id)
        if candidate_profile:
            dao.create_new_cv(candidate_id=candidate_profile.id, title=title, file_path=file_path)
            flash('Tạo CV thành công!', 'success')
            return redirect(url_for('candidate.manage_cvs'))
        else:
            flash('Không tìm thấy hồ sơ ứng viên.', 'danger')

    return render_template('cv_create.html')

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