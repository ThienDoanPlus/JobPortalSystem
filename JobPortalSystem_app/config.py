# File cấu hình app
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# down các biến trong .env
load_dotenv()


class Config:
    """
    Lớp cấu hình, lấy các giá trị từ file .env hoặc sử dụng giá trị mặc định.
    """
    # Lấy SECRET_KEY từ file .env
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Xây dựng chuỗi kết nối cơ sở dữ liệu từ các biến trong .env
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASS')
    host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    encoded_password = quote_plus(password)

    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')


    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{user}:{encoded_password}@{host}/{db_name}'
    SQLALCHEMY_TRACK_MODIFICATIONS = True