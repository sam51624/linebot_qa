import os
import re
from google.cloud import vision

# ✅ ตั้งค่าการเข้าถึง Service Account JSON
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/etc/secrets/credentials.json"

def extract_sku_from_bytes(image_bytes):
    """รับข้อมูลภาพแบบ bytes แล้วตรวจจับรหัสสินค้า (SKU)"""
    client = vision.ImageAnnotatorClient()

    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if not texts:
        return []

    full_text = texts[0].description.strip()
    print("📦 ข้อความที่อ่านได้จากภาพ:\n", full_text)

    # ✅ ดึงเฉพาะรหัสสินค้า 6 หลัก เช่น 030216
    sku_list = re.findall(r"\b\d{6}\b", full_text)

    return sku_list

