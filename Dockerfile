# Sử dụng Python 3.13-slim làm nền tảng
FROM python:3.13-slim

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-cffi \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    libharfbuzz0b \
    libcairo2 \
    libgobject-2.0-0 \
    libffi-dev \
    pkg-config \
    fontconfig \
    && \
    # Xóa cache của apt-get để giữ image gọn nhẹ
    rm -rf /var/lib/apt/lists/*

# Sao chép file requirements.txt vào trước để tận dụng cache của Docker
COPY requirements.txt requirements.txt

# Cài đặt tất cả các thư viện cần thiết từ file requirements
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn của dự án vào container
COPY . .

EXPOSE 5000

CMD ["python", "run.py"]