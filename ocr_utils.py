import os
import base64
import requests
import re
from google.cloud import vision

# ใช้ Service Account JSON จาก Google Cloud
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "credentials.json"

def extract_sku_from_image(image_path):
    client = vision.ImageAnnotatorClient()

    with open(image_path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    # วิเคราะห์ OCR
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if not texts:
        return []

    full_text = texts[0].description.strip()

    # ✅ หาเฉพาะรหัสสินค้า 6 หลัก เช่น 030216, 000632
    sku_list = re.findall(r"\b\d{6}\b", full_text)

    return sku_list
