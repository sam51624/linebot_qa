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

    # ✅ ถ้าไม่พบ context ให้หาสินค้าใกล้เคียงจาก keyword
    if not context:
        similar_context = search_faiss(user_message[:4])
        if similar_context:
            return f"ไม่พบสินค้าตรงกับ: '{user_message}'\nแต่เราแนะนำสินค้าใกล้เคียงดังนี้:\n{similar_context[:1000]}"
        else:
            return f"ขออภัยค่ะ ไม่พบข้อมูลสินค้าสำหรับ: '{user_message}'"

    # ✅ ตัด context ไม่ให้ยาวเกินไป
    context = context[:2000]

    # เตรียมข้อความ
    messages = [{"role": "system", "content": system_message}]

    # ✅ ถ้ามี user_id ให้ดึงประวัติการคุย
    if user_id and user_id in chat_history:
        history = chat_history[user_id][-6:]  # ใช้ 3 คู่สนทนา (user-assistant)
        messages.extend(history)

    # ✅ เพิ่มคำถามล่าสุด
    messages.append({"role": "user", "content": f"ข้อมูลสินค้า:\n{context}\n\nคำถาม:\n{user_message}"})

    # เรียกโมเดล
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
        max_tokens=300
    )

    reply = response.choices[0].message.content.strip()

    # ✅ บันทึกบทสนทนาใหม่เข้า history
    if user_id:
        chat_history.setdefault(user_id, []).append({"role": "user", "content": user_message})
        chat_history[user_id].append({"role": "assistant", "content": reply})
        chat_history[user_id] = chat_history[user_id][-10:]  # จำกัดไม่เกิน 5 รอบบทสนทนา (10 ข้อความ)

    return reply

