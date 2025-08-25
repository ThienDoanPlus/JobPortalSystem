from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from . import dao
from .models import JobPost, RoleEnum, User
from flask_login import current_user, login_required
from flask import current_app


index_bp = Blueprint('main', __name__)

@index_bp.route('/')
def home():
    # Lấy dữ liệu công việc mới nhất
    latest_jobs = dao.get_latest_jobs(limit=8)

    # Lấy từ khóa tìm kiếm từ form
    search_keyword = request.args.get('keyword', '')
    search_location = request.args.get('location', '')
    search_type = request.args.get('search_type', 'all')  # ← Thêm dòng này

    # Nếu có tìm kiếm
    if search_keyword or search_location:
        jobs = dao.search_jobs(
            keyword=search_keyword,
            location=search_location,
            search_type=search_type,
            limit=20
        )
    else:
        jobs = latest_jobs

    return render_template('index.html',
                           latest_jobs=latest_jobs,
                           jobs=jobs,
                           search_keyword=search_keyword,
                           search_location=search_location,
                           search_type=search_type)


@index_bp.route('/jobs')
def job_list():
    """Trang danh sách tất cả công việc, có hỗ trợ tìm kiếm"""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '').strip()
    location = request.args.get('location', '').strip()

    # Gọi DAO để lấy kết quả tìm kiếm có phân trang
    jobs_paginated = dao.search_jobs_paginated(
        keyword=keyword,
        location=location,
        page=page,
        per_page=20
    )

    return render_template('job_list.html',
                           jobs=jobs_paginated,
                           search_keyword=keyword,
                           search_location=location)

# Thêm một route ví dụ khác
@index_bp.route('/job/<int:job_id>')
def job_detail(job_id):
    job = dao.get_job_by_id(job_id)
    if not job:
        flash('Công việc không tồn tại.', 'danger')
        return redirect(url_for('main.home'))

    cv_list = []
    if current_user.is_authenticated and current_user.role.name == 'CANDIDATE':
        profile = dao.get_candidate_profile_by_user_id(current_user.id)
        if profile:
            cv_list = profile.resumes.all()

    return render_template('jobs/job_detail.html',
                           job=job,
                           cv_list=cv_list)



@index_bp.route('/about')
def about():
    return "<h1>Đây là trang giới thiệu</h1>"

# file: index.py

@index_bp.route('/apply/<int:job_id>', methods=['POST'])
@login_required
def apply_job(job_id):
    if current_user.role != RoleEnum.CANDIDATE:
        return jsonify({'error': 'Chỉ có ứng viên mới có thể ứng tuyển.'}), 403

    if not current_user.candidate_profile:
         return jsonify({'error': 'Không tìm thấy hồ sơ ứng viên của bạn.'}), 400

    resume_id = request.form.get('resume_id')
    cv_file   = request.files.get('cv_file')

    # Nếu không chọn CV online và cũng không tải file lên
    if not resume_id and not cv_file:
        return jsonify({'error': 'Vui lòng chọn CV online hoặc tải lên một file CV.'}), 400

    try:
        # Hàm DAO sẽ xử lý tất cả logic
        application = dao.create_application(
            job_id=job_id,
            candidate_id=current_user.candidate_profile.id,
            resume_id=resume_id,
            cv_file=cv_file
        )
        return jsonify({'success': True, 'application_id': application.id})

    except Exception as e:
        # Bắt các lỗi cụ thể từ DAO để trả về thông báo rõ ràng
        # Ví dụ: lỗi đã ứng tuyển, lỗi file không hợp lệ, ...
        # Ghi lại log lỗi để debug
        current_app.logger.error(f"Application Error: {e}")
        return jsonify({'error': str(e)}), 400




