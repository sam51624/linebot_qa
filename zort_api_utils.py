import requests

ZORT_API_URL = "https://open-api.zortout.com/v4"
ZORT_API_KEY = "qQGfmDGZmbjzuYSfPvEE/8f/qBuB7zLbvG8GmKdtM0="
ZORT_API_SECRET = "RC7XffROdRWR/KbziFEdXKHQmhkks3RNwvGcIUZoZ38="
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

    return data["data"][0]  # ดึงสินค้าตัวแรกที่ตรงกับ SKU
