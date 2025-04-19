import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_product(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    name = soup.select_one("h1.product_title").get_text(strip=True)
    code = soup.select_one("span.sku")
    code = code.get_text(strip=True) if code else "ไม่มีรหัส"

    price = soup.select_one("p.price > span > bdi")
    price = price.get_text(strip=True) if price else "ไม่ระบุ"

    img = soup.select_one("figure.woocommerce-product-gallery__wrapper img")
    image_url = img['src'] if img else ""

    return {
        "name": name,
        "code": code,
        "price": price,
        "image_url": image_url,
        "url": url
    }

# 🔁 ทดสอบกับสินค้าเดียว
product_url = "https://www.klongthomshoppingmall.com/product/sfur2005t3d-ball-screw-nut/"
product_data = scrape_product(product_url)

# ✅ ดูตัวอย่าง
df = pd.DataFrame([product_data])
print(df)

