# dao.py
import json
import os

def check_user(username, password):
    # Lấy đường dẫn tuyệt đối tới data.json
    current_dir = os.path.dirname(__file__)
    data_path = os.path.join(current_dir, "data", "data.json")

    with open(data_path, encoding="utf-8") as f:
        users = json.load(f)

    for u in users:
        if u["username"] == username and str(u["password"]) == str(password):
            return True
    return False
