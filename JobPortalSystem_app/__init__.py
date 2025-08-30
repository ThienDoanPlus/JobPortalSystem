# file dùng để chạy app và cấu hình các extension
import os
from urllib.parse import quote

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv
import click


# Khởi tạo các extension
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Vui lòng đăng nhập để xem trang này."
login_manager.login_message_category = "info"
mail = Mail()
load_dotenv()


def create_app(config_class=Config):
    # 2. Tạo instance ứng dụng Flask
    app = Flask(__name__)

    # 3. Tải cấu hình từ lớp Config trong file config.py
    app.config.from_object(config_class)

    # CẤU HÌNH FLASK-MAIL ✅ Thêm đoạn này
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('GMAIL_USERNAME')  # Dùng GMAIL_USERNAME
    app.config['MAIL_PASSWORD'] = os.environ.get('GMAIL_APP_PASSWORD')  # Dùng GMAIL_APP_PASSWORD
    app.config['MAIL_DEFAULT_SENDER'] = ('JobPortal', os.environ.get('GMAIL_USERNAME'))
    # 4. Gắn các extension đã khởi tạo vào ứng dụng
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)  # ✅ Gắn mail
    # 5.  Import models ở đây ĐỂ Flask-Migrate có thể thấy
    with app.app_context():
        from . import models
        from .index import index_bp
        app.register_blueprint(index_bp)

        from .auth import auth_bp
        app.register_blueprint(auth_bp)

        from .candidate import candidate_bp
        app.register_blueprint(candidate_bp)

        from .employer import employer_bp
        app.register_blueprint(employer_bp, url_prefix='/employer')

        from .admin import setup_admin
        setup_admin(app)
        from .api import api_bp
        app.register_blueprint(api_bp)

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    @app.cli.command("create-admin")
    @click.argument("username")
    @click.argument("email")
    @click.argument("password")
    def create_admin_command(username, email, password):
        """Tạo một tài khoản admin mới."""
        from . import dao
        from .models import RoleEnum, User

        if User.query.filter_by(username=username).first():
            print(f"Lỗi: Tên đăng nhập '{username}' đã tồn tại.")
            return
        if User.query.filter_by(email=email).first():
            print(f"Lỗi: Email '{email}' đã được sử dụng.")
            return

        try:
            dao.create_user(
                username=username,
                email=email,
                password=password,
                role=RoleEnum.ADMIN
            )
            print(f"Đã tạo tài khoản admin '{username}' thành công!")
        except Exception as e:
            print(f"Lỗi khi tạo admin: {e}")

    # Tạo template
    @app.cli.command("seed-cv-templates")
    def seed_cv_templates_command():
        from .models import Resume, Experience, Education

        """Tạo các mẫu CV mặc định trong database."""
        print("Bắt đầu tạo các mẫu CV...")
        BLANK_TEMPLATE_NAME = "BLANK_TEMPLATE"

        # Kiểm tra xem mẫu trống đã tồn tại chưa bằng tên
        if not Resume.query.filter_by(template_name=BLANK_TEMPLATE_NAME).first():
            template_blank = Resume(
                is_template=True,
                template_name=BLANK_TEMPLATE_NAME,  # Tên định danh duy nhất
                title="CV Trống",
                thumbnail_url="/static/image/template_blank.jpg"  # Tạo một ảnh thumbnail cho nó
            )
            db.session.add(template_blank)
            print("Đã thêm Mẫu CV Trống.")
        # Mẫu 1: Cổ điển
        template1 = Resume(
            is_template=True,
            template_name="Cổ điển",
            title="Lập trình viên Java",
            thumbnail_url="/static/image/template_classic.jpg",
            font_family="'Times New Roman', serif",
            theme_color="#1a202c"
        )
        exp1 = Experience(job_title="Junior Developer", company_name="Công ty ABC",
                          description="Phát triển và bảo trì các ứng dụng web.")
        edu1 = Education(institution_name="Đại học Quốc Gia", degree="Cử nhân", major="Khoa học Máy tính")
        template1.experiences.append(exp1)
        template1.educations.append(edu1)
        db.session.add(template1)

        # Mẫu 2: Hiện đại
        template2 = Resume(
            is_template=True,
            template_name="Hiện đại",
            title="Chuyên viên Marketing",
            thumbnail_url="/static/image/template_modern.jpg",
            font_family="'Montserrat', sans-serif",
            theme_color="#2C7A7B"
        )
        exp2 = Experience(job_title="Marketing Executive", company_name="Tập đoàn XYZ",
                          description="Lên kế hoạch và thực thi các chiến dịch digital marketing.")
        edu2 = Education(institution_name="Đại học Kinh tế", degree="Cử nhân", major="Marketing")
        template2.experiences.append(exp2)
        template2.educations.append(edu2)
        db.session.add(template2)

        db.session.commit()
        print("Đã tạo thành công 2 mẫu CV.")

    return app
