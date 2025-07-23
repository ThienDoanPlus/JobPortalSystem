# /JobPortalSystem/JobPortalSystem_app/employer.py
from .utils import recruiter_required
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import dao
from .models import ExperienceLevelEnum, JobTypeEnum, JobPost

employer_bp = Blueprint('employer', __name__)



@employer_bp.route('/dashboard')
@login_required
@recruiter_required
def dashboard():
    # Lấy company profile của user đang đăng nhập
    company = dao.get_company_by_user_id(current_user.id)
    jobs = []
    if company:
        # sắp xếp để tin mới nhất lên đầu
        jobs = company.job_posts.order_by(JobPost.created_date.desc()).all()

    return render_template('employer/dashboard.html', company=company, jobs=jobs)

@employer_bp.route('/post-job', methods=['GET', 'POST'])
@login_required
@recruiter_required
def post_job():
    if request.method == 'POST':
        # Lấy company profile của user đang đăng nhập
        company = dao.get_company_by_user_id(current_user.id)
        if not company:
            flash('Không tìm thấy thông tin công ty của bạn.', 'danger')
            return redirect(url_for('main.home'))

        # Lấy dữ liệu từ form
        job_data = {
            "title": request.form.get('title'),
            "job_type": request.form.get('job_type'),
            "experience_level": request.form.get('experience_level'),
            "location": request.form.get('location'),
            "salary_min": request.form.get('salary_min'),
            "salary_max": request.form.get('salary_max'),
            "description": request.form.get('description'),
            "requirements": request.form.get('requirements'),
            "benefits": request.form.get('benefits')
        }

        # Gọi hàm DAO để tạo tin đăng
        dao.create_job_post(company_id=company.id, data=job_data)

        flash('Đăng tin tuyển dụng thành công!', 'success')
        return redirect(url_for('employer.dashboard'))

    return render_template('employer/post_job.html',
                           job_types=JobTypeEnum,
                           experience_levels=ExperienceLevelEnum)


