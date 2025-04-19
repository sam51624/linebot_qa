from openai import OpenAI
import os
from vector_store import search_faiss

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

system_message = """
คุณคือพนักงานขายของร้านคลองถมช้อปปิ้งมอลล์ ให้ข้อมูลสินค้า ตอบคำถามลูกค้า และแนะนำสินค้าที่ใกล้เคียงได้อย่างมืออาชีพ
"""

# เก็บประวัติการคุยของแต่ละ user
chat_history = {}

def answer_question(user_message, user_id=None):
    context = search_faiss(user_message)

    # ✅ ถ้าไม่พบ context ให้หาสินค้าใกล้เคียงจากประวัติ
    if not context and user_id and user_id in chat_history:
        recent_history = chat_history[user_id][-4:]  # ดู 4 ข้อความล่าสุดย้อนหลัง
        for prev in reversed(recent_history):
            if prev["role"] == "user" and any(x in prev["content"] for x in ["รหัส", "ชื่อ", "product", "สินค้า"]):
                context = search_faiss(prev["content"])
                break

    if not context:
        similar_context = search_faiss(user_message[:4])  # ลองหารหัส/ชื่อใกล้เคียง
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
        # บันทึกข้อความล่าสุดไว้
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


