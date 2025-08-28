# /JobPortalSystem/JobPortalSystem_app/employer.py
from .utils import recruiter_required
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from . import dao, momo_service
from .models import ExperienceLevelEnum, JobTypeEnum, JobPost, db, ApplicationStatusEnum, Application, Payment, \
    PaymentStatusEnum
from flask import make_response
from weasyprint import HTML

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
        # 1. Tạo tin tuyển dụng với trạng thái CHỜ (active=False)
        new_job = dao.create_job_post(company_id=company.id, data=job_data, active_status=False)

        # 2. Tạo yêu cầu thanh toán MoMo
        payment_amount = 50000  # Phí đăng tin: 50,000 VND
        order_info = f"Thanh toan phi dang tin: {new_job.title[:50]}"  # MoMo giới hạn độ dài

        # Cần app_context để url_for hoạt động ngoài request context
        with current_app.app_context():
            pay_url, order_id = momo_service.create_momo_payment(payment_amount, order_info)

        if pay_url and order_id:
            # 3. Lưu thông tin giao dịch vào DB
            payment = Payment(id=new_job.id, amount=payment_amount, status=PaymentStatusEnum.PENDING,
                              transaction_id=order_id)
            db.session.add(payment)
            db.session.commit()

            # 4. Chuyển hướng NTD sang trang thanh toán của MoMo
            return redirect(pay_url)
        else:
            flash('Tạo thanh toán không thành công. Vui lòng thử lại.', 'danger')
            db.session.delete(new_job)  # Xóa job đã tạo nếu không tạo được thanh toán
            db.session.commit()
            return redirect(url_for('employer.post_job'))

    return render_template('employer/post_job.html',
                           job_types=JobTypeEnum,
                           experience_levels=ExperienceLevelEnum)

@employer_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@recruiter_required
def settings():
    user = current_user
    profile = getattr(user, 'recruiter_profile', None)

    if request.method == 'POST':
        name = request.form.get('name')
        tax_code = request.form.get('tax_code')
        description = request.form.get('description')
        location = request.form.get('location')
        website = request.form.get('website')

        # Cập nhật bảng Company (recruiter_profile)
        if profile:
            if name:
                profile.name = name
            if tax_code:
                profile.tax_code = tax_code
            if description is not None:
                profile.description = description
            if location is not None:
                profile.location = location
            if website is not None:
                profile.website = website

        # XỬ LÝ ĐỔI MẬT KHẨU
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
            from . import db
            db.session.commit()
            flash('Cập nhật thông tin công ty thành công!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra khi lưu dữ liệu.', 'danger')

        return redirect(url_for('employer.settings'))

    return render_template('employer/employer_settings.html', user=user, profile=profile)

@employer_bp.route('/application/<int:application_id>/update_status', methods=['POST'])
@login_required
@recruiter_required
def update_application_status(application_id):
    app = Application.query.get_or_404(application_id)
    new_status = request.form.get('status')
    if new_status and new_status in ApplicationStatusEnum.__members__:
        app.status = ApplicationStatusEnum[new_status]
        db.session.commit()
        flash('Cập nhật trạng thái thành công!', 'success')
    else:
        flash('Trạng thái không hợp lệ!', 'danger')
    return redirect(request.referrer or url_for('employer.dashboard'))

@employer_bp.route('/<int:cv_id>/preview')
@login_required
@recruiter_required
def preview_candidate_cv(cv_id):
    cv = dao.get_cv_by_id(cv_id)
    print("DEBUG: cv =", cv, flush=True)
    if not cv:
        flash('CV không tồn tại.', 'danger')
        return redirect(url_for('employer.dashboard'))
    return render_template('cv_preview.html', cv=cv)

@employer_bp.route('/cv/<int:cv_id>/download_pdf')
@login_required
@recruiter_required
def download_cv_pdf(cv_id):
    cv = dao.get_cv_by_id(cv_id)
    if not cv:
        flash('CV không tồn tại.', 'danger')
        return redirect(url_for('employer.dashboard'))
    rendered = render_template('cv_preview.html', cv=cv)
    pdf = HTML(string=rendered).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=cv_{cv_id}.pdf'
    return response

@employer_bp.route('/job/<int:job_id>/candidates')
@login_required
@recruiter_required
def view_candidates(job_id):
    job = JobPost.query.get_or_404(job_id)
    applications = job.applications.order_by(db.desc('created_date')).all()
    return render_template(
        'employer/job_candidates.html',
        job=job,
        applications=applications,
        status_choices=ApplicationStatusEnum
    )

# Route mà MoMo sẽ gọi đến server của bạn để báo kết quả (backend-to-backend)
@employer_bp.route('/momo_ipn', methods=['POST'])
def momo_ipn():
    try:
        data = request.json
        result_code = data.get('resultCode')
        order_id = data.get('orderId')

        # TODO: Bắt buộc phải xác thực chữ ký ở môi trường Production

        if result_code == 0:  # Giao dịch thành công
            payment = Payment.query.filter_by(transaction_id=order_id, status=PaymentStatusEnum.PENDING).first()
            if payment:
                payment.status = PaymentStatusEnum.COMPLETED
                job_post = JobPost.query.get(payment.id)
                if job_post:
                    job_post.active = True
                db.session.commit()
                current_app.logger.info(f"Kich hoat thanh cong tin dang ID: {job_post.id}")
    except Exception as e:
        current_app.logger.error(f"Loi xu ly IPN: {e}")

    # Luôn trả về 204 để MoMo biết đã nhận được IPN
    return '', 204

# Route mà người dùng được chuyển về từ MoMo
@employer_bp.route('/momo_return')
@login_required
@recruiter_required
def momo_return():
    result_code = request.args.get('resultCode')
    if result_code == '0':
        flash('Giao dịch đã được ghi nhận. Tin đăng sẽ được kích hoạt sau vài phút.', 'success')
    else:
        flash('Giao dịch không thành công hoặc đã bị hủy.', 'danger')
    return redirect(url_for('employer.dashboard'))


@employer_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@recruiter_required
def settings():
    user = current_user
    profile = getattr(user, 'recruiter_profile', None)

    if request.method == 'POST':
        name = request.form.get('name')
        tax_code = request.form.get('tax_code')
        description = request.form.get('description')
        location = request.form.get('location')
        website = request.form.get('website')

        # Cập nhật bảng Company (recruiter_profile)
        if profile:
            if name:
                profile.name = name
            if tax_code:
                profile.tax_code = tax_code
            if description is not None:
                profile.description = description
            if location is not None:
                profile.location = location
            if website is not None:
                profile.website = website

        # XỬ LÝ ĐỔI MẬT KHẨU
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
            from . import db
            db.session.commit()
            flash('Cập nhật thông tin công ty thành công!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra khi lưu dữ liệu.', 'danger')

        return redirect(url_for('employer.settings'))

    return render_template('employer/employer_settings.html', user=user, profile=profile)

@employer_bp.route('/application/<int:application_id>/update_status', methods=['POST'])
@login_required
@recruiter_required
def update_application_status(application_id):
    app = Application.query.get_or_404(application_id)
    new_status = request.form.get('status')
    if new_status and new_status in ApplicationStatusEnum.__members__:
        app.status = ApplicationStatusEnum[new_status]
        db.session.commit()
        flash('Cập nhật trạng thái thành công!', 'success')
    else:
        flash('Trạng thái không hợp lệ!', 'danger')
    return redirect(request.referrer or url_for('employer.dashboard'))

@employer_bp.route('/<int:cv_id>/preview')
@login_required
@recruiter_required
def preview_candidate_cv(cv_id):
    cv = dao.get_cv_by_id(cv_id)
    print("DEBUG: cv =", cv, flush=True)
    if not cv:
        flash('CV không tồn tại.', 'danger')
        return redirect(url_for('employer.dashboard'))
    return render_template('cv_preview.html', cv=cv)

@employer_bp.route('/cv/<int:cv_id>/download_pdf')
@login_required
@recruiter_required
def download_cv_pdf(cv_id):
    cv = dao.get_cv_by_id(cv_id)
    if not cv:
        flash('CV không tồn tại.', 'danger')
        return redirect(url_for('employer.dashboard'))
    rendered = render_template('cv_preview.html', cv=cv)
    pdf = HTML(string=rendered).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=cv_{cv_id}.pdf'
    return response

@employer_bp.route('/job/<int:job_id>/candidates')
@login_required
@recruiter_required
def view_candidates(job_id):
    job = JobPost.query.get_or_404(job_id)
    applications = job.applications.order_by(db.desc('created_date')).all()
    return render_template(
        'employer/job_candidates.html',
        job=job,
        applications=applications,
        status_choices=ApplicationStatusEnum
    )

@employer_bp.route('/job/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
@recruiter_required
def edit_job(job_id):
    job = JobPost.query.get_or_404(job_id)
    if request.method == 'POST':
        job.title = request.form['title']
        job.job_type = JobTypeEnum[request.form['job_type']]
        job.experience_level = ExperienceLevelEnum[request.form['experience_level']]
        job.location = request.form['location']
        job.salary_min = request.form['salary_min']
        job.salary_max = request.form['salary_max']
        job.description = request.form['description']
        job.requirements = request.form['requirements']
        job.benefits = request.form['benefits']
        db.session.commit()
        flash('Cập nhật thành công!', 'success')
        return redirect(url_for('employer.dashboard'))
    return render_template(
        'employer/edit_job.html',
        job=job,
        job_types=JobTypeEnum,
        experience_levels=ExperienceLevelEnum
    )

@employer_bp.route('/job/<int:job_id>/delete', methods=['POST'])
@login_required
@recruiter_required
def delete_job(job_id):
    job = JobPost.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('Đã xoá bài đăng thành công!', 'success')
    return redirect(url_for('employer.dashboard'))


@employer_bp.route('/job/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
@recruiter_required
def edit_job(job_id):
    job = JobPost.query.get_or_404(job_id)
    if request.method == 'POST':
        job.title = request.form['title']
        job.job_type = JobTypeEnum[request.form['job_type']]
        job.experience_level = ExperienceLevelEnum[request.form['experience_level']]
        job.location = request.form['location']
        job.salary_min = request.form['salary_min']
        job.salary_max = request.form['salary_max']
        job.description = request.form['description']
        job.requirements = request.form['requirements']
        job.benefits = request.form['benefits']
        db.session.commit()
        flash('Cập nhật thành công!', 'success')
        return redirect(url_for('employer.dashboard'))
    return render_template(
        'employer/edit_job.html',
        job=job,
        job_types=JobTypeEnum,
        experience_levels=ExperienceLevelEnum
    )

@employer_bp.route('/job/<int:job_id>/delete', methods=['POST'])
@login_required
@recruiter_required
def delete_job(job_id):
    job = JobPost.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('Đã xoá bài đăng thành công!', 'success')
    return redirect(url_for('employer.dashboard'))

@employer_bp.route('/stats')
@login_required
@recruiter_required
def stats():
    company = current_user.recruiter_profile
    jobs = JobPost.query.filter_by(company_id=company.id).all()
    # Tạo dict: job_id -> số lượng ứng viên
    stats_data = []
    for job in jobs:
        stats_data.append({
            'job': job,
            'app_count': job.applications.count()
        })
    return render_template('employer/stats.html', stats_data=stats_data)
