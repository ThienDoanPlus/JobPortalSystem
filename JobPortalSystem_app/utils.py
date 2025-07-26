# File tien ich chung
# /JobPortalSystem/JobPortalSystem_app/utils.py

from flask import flash, redirect, url_for
from flask_login import current_user
from functools import wraps
from flask import current_app, render_template
from flask_mail import Message
import threading
from . import mail, db
from .models import Application
"""
    decorator để đảm bảo người dùng đã đăng nhập và có vai trò là RECRUITER.
"""
def recruiter_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Kiểm tra xem user có được xác thực
        if not current_user.is_authenticated or current_user.role.name != 'RECRUITER':
            flash('Bạn không có quyền truy cập trang này.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function


def send_async_email(app, msg):
    """Hàm chạy trong thread để gửi mail mà không block request."""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Lỗi khi gửi email: {e}")

def send_application_emails(application_id):
    """
    Chuẩn bị và gửi email xác nhận cho cả ứng viên và nhà tuyển dụng dựa trên application_id.
    """
    app = current_app._get_current_object()

    # Truy vấn application với quan hệ 'candidate' và 'job' được tải
    # SỬA Ở ĐÂY: Dùng .candidate thay vì .candidate_profile
    application = db.session.query(Application).options(
        db.joinedload(Application.candidate),
        db.joinedload(Application.job)
    ).filter_by(id=application_id).first()

    if not application:
        app.logger.error(f"Không tìm thấy application với ID {application_id}")
        return

    # SỬA Ở ĐÂY: Dùng application.candidate
    candidate = application.candidate
    if not candidate or not candidate.user or not candidate.user.email:
        app.logger.error(f"Không thể gửi email cho ứng viên: {candidate}")
        return

    job = application.job
    recruiter_user = job.company.user if job and job.company else None
    if not recruiter_user or not recruiter_user.email:
        app.logger.error(f"Không thể gửi email cho nhà tuyển dụng: {job.company if job else None}")
        return

    # 1. Chuẩn bị email cho ứng viên
    candidate_msg = Message(
        subject="JobPortal Xác nhận ứng tuyển thành công",
        recipients=[candidate.user.email]  # SỬA Ở ĐÂY
    )
    candidate_msg.html = render_template(
        'emails/candidate_confirmation.html',
        candidate_name=candidate.full_name or "Ứng viên", # SỬA Ở ĐÂY
        job_title=job.title,
        company_name=job.company.name or "Công ty không xác định"
    )
    try:
        threading.Thread(target=send_async_email, args=(app, candidate_msg)).start()
    except Exception as e:
        app.logger.error(f"Lỗi gửi email cho ứng viên: {str(e)}")

    # 2. Chuẩn bị email cho nhà tuyển dụng
    website_name = app.config.get('WEBSITE_NAME', 'JobPortal')
    recruiter_msg = Message(
        subject=f"[{website_name}] Có ứng viên mới cho vị trí {job.title}",
        recipients=[recruiter_user.email]
    )
    recruiter_msg.html = render_template(
        'emails/recruiter_notification.html',
        job_title=job.title,
        candidate_name=candidate.full_name or "Ứng viên", # SỬA Ở ĐÂY
        candidate_email=candidate.user.email, # SỬA Ở ĐÂY
        candidate_phone=candidate.phone_number or "Chưa cung cấp" # SỬA Ở ĐÂY
    )
    try:
        threading.Thread(target=send_async_email, args=(app, recruiter_msg)).start()
    except Exception as e:
        app.logger.error(f"Lỗi gửi email cho nhà tuyển dụng: {str(e)}")