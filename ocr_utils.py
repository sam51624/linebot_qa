import re
from google.cloud import vision

def extract_sku_from_image_bytes(image_bytes):
    """
    วิเคราะห์ภาพด้วย OCR จาก Google Cloud Vision
    และดึงรหัสสินค้า 6 หลักจากข้อความในภาพ

    Args:
        image_bytes (bytes): เนื้อหาภาพ

    Returns:
        list[str]: รหัสสินค้า เช่น ["000632", "123456"]
    """
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if not texts:
        return []

    full_text = texts[0].description.strip()
    print("🧠 OCR Text:", full_text)

    # ดึงรหัส 6 หลัก (ตัวเลข)
    sku_list = re.findall(r"\b\d{6}\b", full_text)

    return sku_list
