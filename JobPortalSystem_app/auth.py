from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import dao
from .models import RoleEnum
from flask_login import login_user, logout_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Lấy các trường chung
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        role_str = request.form.get('role')

        # Kiểm tra xem user đã tồn tại chưa
        if dao.get_user_by_username(username):
            flash('Tên đăng nhập đã tồn tại.', 'danger')
            return render_template('register.html')  # Quay lại form với dữ liệu đã nhập

        # Xử lý theo vai trò
        try:
            role = RoleEnum[role_str.upper()]
            if role == RoleEnum.CANDIDATE:
                full_name = request.form.get('full_name')
                if not full_name:
                    raise ValueError("Họ và tên là bắt buộc cho ứng viên.")
                dao.create_user(username=username, email=email, password=password,
                                role=role, full_name=full_name)

            elif role == RoleEnum.RECRUITER:
                company_name = request.form.get('company_name')
                if not company_name:
                    raise ValueError("Tên công ty là bắt buộc cho nhà tuyển dụng.")
                dao.create_user(username=username, email=email, password=password,
                                role=role, company_name=company_name)

            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('auth.login'))

        except (KeyError, ValueError) as e:
            flash(str(e), 'danger')

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.get_user_by_username(username)

        # Kiểm tra user và mật khẩu
        if user and dao.check_password(user, password):
            # BƯỚC 2: NẾU ĐÚNG, THỰC HIỆN ĐĂNG NHẬP
            login_user(user)
            flash('Đăng nhập thành công!', 'success')

            # BƯỚC 3: KIỂM TRA VAI TRÒ ĐỂ CHUYỂN HƯỚNG
            if user.role == RoleEnum.ADMIN:
                return redirect(url_for('admin.index'))
            else:
                return redirect(url_for('main.home'))
        else:
            # BƯỚC 4: NẾU SAI, THÔNG BÁO LỖI
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
            # Quay lại trang login để người dùng thử lại
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))