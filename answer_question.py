from openai import OpenAI
import os
import re
from vector_store import search_faiss
from data_loader import load_data_from_sheet

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

system_message = """
คุณคือพนักงานขายของร้านคลองถมช้อปปิ้งมอลล์ ให้ข้อมูลสินค้า ตอบคำถามลูกค้า และแนะนำสินค้าที่ใกล้เคียงได้อย่างมืออาชีพ
"""

# เก็บประวัติการคุยของแต่ละ user
chat_history = {}

def get_product_info_from_sheet(product_code):
    df = load_data_from_sheet()
    product_code = str(product_code).strip()
    row = df[df["รหัสสินค้า"].astype(str).str.strip() == product_code]
    if not row.empty:
        name = row.iloc[0]["ชื่อสินค้า"]
        price = row.iloc[0]["ราคาขาย"]
        qty = row.iloc[0]["จำนวนพร้อมขาย"]
        return f"รหัสสินค้า {product_code} คือ {name} ราคาขาย {price:.2f} บาท คงเหลือ {qty} ชิ้น"
    else:
        return None

def answer_question(user_message, user_id=None):
    # ✅ ถ้าพบคำถามเกี่ยวกับราคา/สินค้า → ดึงจาก Google Sheet โดยตรง
    if re.search(r"(ราคาเท่าไหร่|ราคา[ ]*สินค้า|ราคาของ|มีของมั้ย|มีของไหม|มีสินค้าไหม|มีสินค้ามั้ย)", user_message):
        found_code = re.search(r"\b\d{6}\b", user_message)
        if found_code:
            code = found_code.group()
            product_info = get_product_info_from_sheet(code)
            if product_info:
                return product_info

    context = search_faiss(user_message)

    # ✅ ถ้าไม่พบ context ให้หาสินค้าใกล้เคียงจาก keyword
    if not context:
        similar_context = search_faiss(user_message[:4])
        if similar_context:
            return f"ไม่พบสินค้าตรงกับ: '{user_message}'\nแต่เราแนะนำสินค้าใกล้เคียงดังนี้:\n{similar_context[:1000]}"
        else:
            return f"ขออภัยค่ะ ไม่พบข้อมูลสินค้าสำหรับ: '{user_message}'"

    # ✅ ตัด context ไม่ให้ยาวเกินไป
    context = context[:2000]

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"ข้อมูลสินค้า:\n{context}\n\nคำถาม:\n{user_message}"}
    ]

    # เพิ่มประวัติการคุย (chat memory)
    if user_id:
        user_chat = chat_history.get(user_id, [])[-3:]  # เอาแค่ล่าสุด 3 ข้อความ
        for m in user_chat:
            messages.insert(-1, m)  # แทรกก่อน user message ล่าสุด
        chat_history.setdefault(user_id, []).append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
        max_tokens=300
    )

    reply = response.choices[0].message.content.strip()

    # บันทึกคำตอบลงประวัติด้วย
    if user_id:
        chat_history[user_id].append({"role": "assistant", "content": reply})

    return reply


