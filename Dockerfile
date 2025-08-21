# Sử dụng một image Python 3.9 gọn nhẹ làm nền tảng
FROM python:3.9-slim

# Thiết lập thư mục làm việc bên trong container là /app
WORKDIR /app

# Sao chép file requirements.txt vào trước để tận dụng cache
COPY requirements.txt requirements.txt

# Cài đặt tất cả các thư viện Python cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn của dự án vào container
COPY . .

# Mở cổng 5000 để bên ngoài có thể truy cập vào ứng dụng
EXPOSE 5000

# Lệnh mặc định để chạy ứng dụng khi container khởi động
CMD ["python", "run.py"]