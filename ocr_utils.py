import os
import re
from google.cloud import vision

# ✅ ระบุ path ไปยัง service account credentials (จะถูก mount ไว้ใน Cloud Run)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/etc/secrets/credentials.json"

def extract_info_from_image_bytes(image_bytes):
    client = vision.ImageAnnotatorClient()

    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    annotations = response.text_annotations

    if not annotations:
        return []

    full_text = annotations[0].description.strip()
    print("🧠 OCR full text:", full_text)

    # ✅ หารหัสสินค้า (SKU 6 หลัก) เช่น 000123
    sku_matches = re.findall(r"\b\d{6}\b", full_text)

    # ✅ แยกบรรทัดเพื่อดึงชื่อสินค้าแบบละเอียด
    lines = full_text.splitlines()
    product_names = []
    for line in lines:
        if len(line.strip()) > 6 and not re.search(r"\b\d{6}\b", line):
            product_names.append(line.strip())

    # ✅ รวมผลลัพธ์เป็น list ของ dict
    results = []
    for i, sku in enumerate(sku_matches):
        results.append({
            "sku": sku,
            "name": product_names[i] if i < len(product_names) else None
        })

    # ถ้าไม่มี sku แต่มีชื่อสินค้า → คืนชื่อสินค้าอย่างเดียว
    if not results and product_names:
        for name in product_names:
            results.append({
                "sku": None,
                "name": name
            })

    return results

