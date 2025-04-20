import os
import base64
import requests
from google.cloud import vision

# ใช้ Service Account JSON จาก Google Cloud
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

def extract_text_from_image(image_url):
    client = vision.ImageAnnotatorClient()

    # ดึงภาพจาก URL
    response = requests.get(image_url)
    content = response.content
    image = vision.Image(content=content)

    # วิเคราะห์ OCR
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        return texts[0].description.strip()
    return ""
