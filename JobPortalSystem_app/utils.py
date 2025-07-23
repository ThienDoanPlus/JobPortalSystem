# File tien ich chung
# /JobPortalSystem/JobPortalSystem_app/utils.py

from flask import flash, redirect, url_for
from flask_login import current_user
from functools import wraps
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

