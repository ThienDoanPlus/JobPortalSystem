# Sử dụng Python 3.10 làm nền tảng
FROM python:3.13-slim

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Sao chép file requirements.txt vào trước để tận dụng cache của Docker
COPY requirements.txt requirements.txt

# Cài đặt tất cả các thư viện cần thiết từ file requirements
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn của dự án vào container
COPY . .

# Mở cổng 5000 để ứng dụng có thể được truy cập từ bên ngoài
EXPOSE 5000

# Lệnh mặc định để chạy ứng dụng khi container khởi động
CMD ["python", "run.py"]