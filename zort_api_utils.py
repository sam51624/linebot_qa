import requests

ZORT_API_URL = "https://open-api.zortout.com/v4"
ZORT_API_KEY = "78M7bVcPOWWk1Tcx0MhEjsAg3UrJuikhLtg0F6gBJHo="
ZORT_API_SECRET = "AsL9e8EfmGpt5JlMnxgOUjFRX4P974wUPS7WvcG1xI="
STORE_NAME = "klongthomshopping@gmail.com"

def get_access_token():
    url = f"{ZORT_API_URL}/token"
    payload = {
        "username": STORE_NAME,
        "apiKey": ZORT_API_KEY,
        "apiSecret": ZORT_API_SECRET
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    data = response.json()
    return data["accessToken"]

def search_product_by_sku(sku: str):
    try:
        token = get_access_token()
        url = f"{ZORT_API_URL}/product/search"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        params = {
            "keyword": sku,
            "page": 1,
            "limit": 1
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "success" or not data.get("data"):
            return None

        return data["data"][0]  # ดึงสินค้าตัวแรก
    except Exception as e:
        print(f"❌ ไม่สามารถเชื่อมต่อ Zort API: {e}")
        return None

def format_product_reply(product):
    sku = product.get("code", "ไม่ระบุ")
    name = product.get("name", "ไม่ระบุ")
    price = product.get("price", "ไม่ระบุ")

    return f"""🔎 รหัสสินค้า: {sku}
📦 ชื่อสินค้า: {name}
💰 ราคาขาย: {price} บาท
📌 ราคานี้ยังไม่รวมค่าจัดส่งสินค้าและภาษี Vat 7%"""

