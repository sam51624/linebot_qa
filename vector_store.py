from data_loader import load_data_from_sheet

def search_faiss(query):
    df = load_data_from_sheet()
    result = []

    for _, row in df.iterrows():
        # ตรวจสอบคอลัมน์ว่าว่างหรือไม่ก่อนใช้งาน
        name = str(row.get("ชื่อสินค้า", "")).strip()
        code = str(row.get("รหัสสินค้า", "")).strip()
        price = str(row.get("ราคาขาย", "")).strip()
        qty = str(row.get("จำนวน", "")).strip()

        text = f"{name} (รหัส {code}) - ราคา {price} บาท - เหลือ {qty} ชิ้น"
        if query.lower() in text.lower():
            result.append(text)

    return "\n".join(result) if result else "ขออภัยค่ะ ไม่พบสินค้าที่คุณถามมาในระบบ"
