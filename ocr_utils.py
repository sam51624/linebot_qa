import io
import re
from google.cloud import vision

def extract_info_from_image_bytes(image_bytes):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if not texts:
        return [], []

    full_text = texts[0].description
    lines = full_text.splitlines()

    sku_list = []
    name_list = []

    for line in lines:
        if re.search(r"\b\d{5,}\b", line):
            sku_list.append(line.strip())
        elif any(keyword in line.lower() for keyword in ["motor", "gearbox", "profile", "controller", "sensor", "wire"]):
            name_list.append(line.strip())

    return sku_list, name_list
