# file dùng để chạy app và cấu hình các extension
import os
from urllib.parse import quote

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from flask_login import LoginManager
from flask_mail import Mail             # ✅ Thêm
from dotenv import load_dotenv          # ✅ Thêm

# Khởi tạo các extension
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Vui lòng đăng nhập để xem trang này."
login_manager.login_message_category = "info"

mail = Mail()  # ✅ Thêm

load_dotenv()  # ✅ Nạp biến môi trường từ .env

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
    from . import models
    from .index import index_bp
    app.register_blueprint(index_bp)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .candidate import candidate_bp
    app.register_blueprint(candidate_bp)

    from .employer import employer_bp
    app.register_blueprint(employer_bp, url_prefix='/employer')


    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])


    return app