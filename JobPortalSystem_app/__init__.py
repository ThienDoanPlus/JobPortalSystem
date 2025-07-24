# file dùng để chạy app và cấu hình các extension
import os
from urllib.parse import quote

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from flask_login import LoginManager

# Khởi tạo các extension
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Vui lòng đăng nhập để xem trang này."
login_manager.login_message_category = "info"

def create_app(config_class=Config):
    # 2. Tạo instance ứng dụng Flask
    app = Flask(__name__)

    # 3. Tải cấu hình từ lớp Config trong file config.py
    app.config.from_object(config_class)

    # 4. Gắn các extension đã khởi tạo vào ứng dụng
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    # 5.  Import models ở đây ĐỂ Flask-Migrate có thể thấy
    from . import models
    from .index import index_bp
    app.register_blueprint(index_bp)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .candidate import candidate_bp
    app.register_blueprint(candidate_bp)

    from .employer import employer_bp
    app.register_blueprint(employer_bp)


    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])


    return app