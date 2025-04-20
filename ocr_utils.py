# 📁 ocr_utils.py

import os
import requests
import re
from google.cloud import vision

# ✅ กำหนด path ไปยัง credentials.json (Service Account จาก Google Cloud)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "credentials.json"

def extract_sku_from_image_url(image_url):
    """
    ดึงข้อความจากภาพด้วย OCR ผ่าน Google Cloud Vision API
    และค้นหารหัสสินค้า (SKU) แบบตัวเลข 6 หลัก

    Args:
        image_url (str): URL จาก LINE API

    Returns:
        list[str]: รายการรหัสสินค้าที่เจอ (เช่น ["000632", "123456"])
    """
    # เรียกใช้ LINE API ดึงเนื้อหาภาพ
    headers = {
        "Authorization": f"Bearer {os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')}"
    }
    response = requests.get(image_url, headers=headers)

    if response.status_code != 200:
        print("❌ ไม่สามารถดึงภาพจาก URL ได้")
        return []

    # เรียกใช้งาน Google Cloud Vision
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=response.content)

    ocr_response = client.text_detection(image=image)
    texts = ocr_response.text_annotations

    if not texts:
        return []

    full_text = texts[0].description.strip()
    print("🧠 OCR Text:", full_text)

    # ✅ ดึงเฉพาะรหัส 6 หลักที่เป็นตัวเลข เช่น 030216
    sku_list = re.findall(r"\b\d{6}\b", full_text)

    return sku_list

