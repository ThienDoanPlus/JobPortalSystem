import os
import json

def check_user(username, password):
    try:
        # Dùng path tuyệt đối dựa vào workspace gốc (Jenkins chạy từ đó)
        data_path = os.path.join("JobPortalSystem_app", "data", "data.json")

        # Kiểm tra tồn tại
        if not os.path.exists(data_path):
            # fallback nếu đang chạy trong PyCharm (dao.py nội bộ gọi)
            current_dir = os.path.dirname(__file__)
            data_path = os.path.join(current_dir, "data", "data.json")

        print(f"[DEBUG] Using data file: {data_path}")

        with open(data_path, encoding="utf-8") as f:
            users = json.load(f)

        for u in users:
            if u["username"] == username and str(u["password"]) == str(password):
                return True
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
