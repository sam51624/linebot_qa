# 📁 ocr_utils.py
import os
import requests
import re
from google.cloud import vision

# ✅ ตั้งค่าตำแหน่งไฟล์ credentials จาก Google Cloud
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "credentials.json"

def extract_sku_from_image_url(image_url):
    client = vision.ImageAnnotatorClient()

    # ดึงภาพจาก URL (LINE message content)
    headers = {
        "Authorization": f"Bearer {os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')}"
    }
    response = requests.get(image_url, headers=headers)
    image = vision.Image(content=response.content)

    # 🔍 ตรวจข้อความในภาพด้วย OCR
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if not texts:
        return []

    full_text = texts[0].description.strip()
    print("🔍 Extracted text from image:", full_text)

    # ✅ ดึงรหัสสินค้า 6 หลัก เช่น 000632, 123456
    sku_list = re.findall(r"\b\d{6}\b", full_text)

    return sku_list
