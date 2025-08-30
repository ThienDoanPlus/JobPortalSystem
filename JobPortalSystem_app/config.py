# File cấu hình app
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load biến từ .env (chỉ áp dụng ở local/dev)
load_dotenv()

class Config:
    """
    Lớp cấu hình cho ứng dụng.
    """
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret')

    UPLOAD_FOLDER = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'static/uploads'
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Chọn DB dựa trên môi trường
    if 'JENKINS_HOME' in os.environ:
        # CI/CD dùng SQLite
        print("--- RUNNING IN CI/CD ENVIRONMENT, USING SQLITE ---")
        SQLALCHEMY_DATABASE_URI = 'sqlite:///ci_app.db'
    else:
        # Development / Production: MySQL
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASS', '')  # nếu chưa set thì rỗng
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '3306')
        database = os.getenv('DB_NAME', 'jobportal')

        encoded_password = quote_plus(password) if password else ''

        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{database}"
        )


class TestingConfig(Config):
    """
    Cấu hình riêng cho test (pytest).
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-memory DB
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
