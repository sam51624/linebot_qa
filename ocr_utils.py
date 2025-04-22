from google.cloud import vision
import io
import re

def extract_text_from_image(image_bytes):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if not texts:
        return "", []

    full_text = texts[0].description
    return full_text, texts

def extract_sku_and_name_from_bytes(image_bytes):
    text, _ = extract_text_from_image(image_bytes)

    lines = text.splitlines()
    sku_candidates = []
    name_lines = []

    for line in lines:
        line = line.strip()

        # หา SKU ด้วย regex
        sku_match = re.findall(r'\b(0?\d{5,7})\b', line)
        if sku_match:
            sku_candidates.extend(sku_match)
            continue

        # ข้าม label ทั่วไป
        if "SKU" in line.upper() or "CODE" in line.upper():
            continue

        # ชื่อสินค้า (อาจหลายบรรทัด)
        name_lines.append(line)

    # สมมุติว่า บรรทัดแรกๆ เป็นชื่อสินค้า
    product_name = " ".join(name_lines[:2]) if name_lines else None
    sku_list = list(set(sku_candidates))

    return sku_list, product_name
