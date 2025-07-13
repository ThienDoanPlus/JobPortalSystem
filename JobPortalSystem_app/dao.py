import os
import json

def check_user(username, password):
    try:
        # Đường dẫn mặc định dùng cho Jenkins
        data_path = os.path.join("JobPortalSystem_app", "data", "data.json")

        # Nếu không tồn tại, dùng fallback (khi chạy local)
        if not os.path.exists(data_path):
            current_dir = os.path.dirname(__file__)
            data_path = os.path.join(current_dir, "data", "data.json")

        print(f"[DEBUG] Using data file: {data_path}")

        with open(data_path, encoding="utf-8") as f:
            users = json.load(f)

        for u in users:
            # So sánh đúng kiểu: username là str, password là int
            if u["username"] == username and u["password"] == password:
                return True
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
