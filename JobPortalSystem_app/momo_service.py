# /JobPortalSystem/JobPortalSystem_app/momo_service.py
import os
import uuid
import hmac
import hashlib
import json
import requests
from flask import url_for


def create_momo_payment(amount, order_info):
    """
    Tạo yêu cầu thanh toán và trả về (URL thanh toán của MoMo, order_id của chúng ta).
    """
    endpoint = os.getenv('MOMO_ENDPOINT')

    partner_code = os.getenv('MOMO_PARTNER_CODE')
    access_key = os.getenv('MOMO_ACCESS_KEY')
    secret_key = os.getenv('MOMO_SECRET_KEY')

    # Khi test local dùng ngrok (phải có NGROK_URL)
    redirect_url = url_for('employer.momo_return', _external=True)
    ipn_url = url_for('employer.momo_ipn', _external=True)

    if "127.0.0.1" in ipn_url or "localhost" in ipn_url:
        ngrok_url = os.getenv('NGROK_URL')
        if ngrok_url:
            redirect_url = redirect_url.replace("http://127.0.0.1:2004", ngrok_url)
            ipn_url = ipn_url.replace("http://127.0.0.1:2004", ngrok_url)
        else:
            print("⚠️ CẢNH BÁO: Không tìm thấy NGROK_URL. IPN của MoMo sẽ không hoạt động ở local.")

    amount_str = str(int(amount))
    order_id = str(uuid.uuid4())
    request_id = str(uuid.uuid4())
    request_type = "captureWallet"
    extra_data = ""

    # --- CHỖ QUAN TRỌNG: rawSignature phải đúng thứ tự ---
    raw_signature_str = (
        f"accessKey={access_key}"
        f"&amount={amount_str}"
        f"&extraData={extra_data}"
        f"&ipnUrl={ipn_url}"
        f"&orderId={order_id}"
        f"&orderInfo={order_info}"
        f"&partnerCode={partner_code}"
        f"&redirectUrl={redirect_url}"
        f"&requestId={request_id}"
        f"&requestType={request_type}"
    )

    signature = hmac.new(
        secret_key.encode('utf-8'),
        raw_signature_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    payload = {
        'partnerCode': partner_code,
        'requestId': request_id,
        'amount': amount_str,
        'orderId': order_id,
        'orderInfo': order_info,
        'redirectUrl': redirect_url,
        'ipnUrl': ipn_url,
        'lang': 'vi',
        'extraData': extra_data,
        'requestType': request_type,
        'signature': signature
    }

    # --- DEBUG ---
    print("\n" + "=" * 50)
    print("CHUẨN BỊ GỬI REQUEST ĐẾN MOMO")
    print(f"Endpoint: {endpoint}")
    print("rawSignature:", raw_signature_str)
    print("Payload (Dữ liệu gửi đi):")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("=" * 50 + "\n")

    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        if response.status_code != 200:
            print("MOMO TRẢ VỀ LỖI:")
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")

        response.raise_for_status()
        result = response.json()
        if result.get('resultCode') == 0:
            return result.get('payUrl'), order_id
        else:
            print(f"Lỗi từ MoMo: {result.get('message')}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API MoMo: {e}")
        return None, None
