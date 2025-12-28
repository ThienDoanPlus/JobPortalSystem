import os
from urllib.parse import quote

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config, TestingConfig
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

# Dictionary để map tên môi trường với Class cấu hình
config_by_name = dict(
    development=Config,
    testing=TestingConfig
)


def create_app(config_name='development'):
    """
    Factory function để tạo và cấu hình ứng dụng Flask.
    """
    app = Flask(__name__)

    # --- SỬA LẠI LOGIC NẠP CONFIG ---
    # 1. Lấy ra ĐỐI TƯỢNG config từ dictionary dựa trên TÊN config
    config_class = config_by_name.get(config_name)
    if not config_class:
        raise ValueError(f"Config '{config_name}' not found. Available configs: {list(config_by_name.keys())}")

    # 2. Tải cấu hình từ ĐỐI TƯỢNG đã lấy được
    app.config.from_object(config_class)

    # Cấu hình Flask-Mail (giữ nguyên)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('GMAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('GMAIL_APP_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = ('JobPortal', os.environ.get('GMAIL_USERNAME'))

    # Gắn các extension vào ứng dụng
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    # --- BỔ SUNG user_loader (RẤT QUAN TRỌNG) ---
    # Hàm này giúp Flask-Login nạp lại user từ session
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Đăng ký Blueprints và các thành phần khác (giữ nguyên)
    with app.app_context():
        from . import models  # Import models để Flask-Migrate nhận diện

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

    # Các lệnh CLI (giữ nguyên)
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

    @app.cli.command("seed-cv-templates")
    def seed_cv_templates_command():
        from .models import Resume, Experience, Education
        """Tạo các mẫu CV mặc định trong database."""
        print("Bắt đầu tạo các mẫu CV...")
        # ... (logic tạo template giữ nguyên) ...
        db.session.commit()
        print("Đã tạo thành công các mẫu CV.")

    return app
