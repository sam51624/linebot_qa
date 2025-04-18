from data_loader import load_data_from_sheet

def search_faiss(query):
    df = load_data_from_sheet()
    result = []

    query_words = query.lower().split()

    for _, row in df.iterrows():
        # รวมคีย์เวิร์ดจากหลายคอลัมน์
        searchable_text = " ".join([
            str(row.get("ชื่อสินค้า", "")),
            str(row.get("รหัสสินค้า", "")),
            str(row.get("Tag", "")),
            str(row.get("หมวดหมู่", "")),
            str(row.get("หมวดหมู่ย่อย", "")),
        ]).lower()

        # ตรวจสอบว่าอย่างน้อยหนึ่งคำใน query อยู่ใน searchable_text
        if any(word in searchable_text for word in query_words):
            name = str(row.get("ชื่อสินค้า", "-"))
            code = str(row.get("รหัสสินค้า", "-"))
            tag = str(row.get("Tag", "-"))
            qty = float(row.get("จำนวน", 0))
            price = str(row.get("ราคาขาย", "-"))

            stock_status = f"คงเหลือ {qty} ชิ้น" if qty > 0 else "สินค้าหมด"
            item_text = f"{name} (รหัส {code}, Tag: {tag}) - ราคา {price} บาท - {stock_status}"
            result.append(item_text)

    return "\n".join(result) if result else "ขออภัยค่ะ ไม่พบข้อมูลสินค้าที่คุณสอบถามมาในระบบค่ะ"

