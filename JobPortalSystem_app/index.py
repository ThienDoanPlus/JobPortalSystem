
from flask import Blueprint, render_template

index_bp = Blueprint('main', __name__)

@index_bp.route('/')
def home():
    return render_template('index.html')

# Thêm một route ví dụ khác
@index_bp.route('/about')
def about():
    return "<h1>Đây là trang giới thiệu</h1>"

