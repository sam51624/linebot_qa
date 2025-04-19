from openai import OpenAI
import os
from vector_store import search_faiss

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

system_message = """
คุณคือพนักงานขายของร้านคลองถมช้อปปิ้งมอลล์ ให้ข้อมูลสินค้า ตอบคำถามลูกค้า และแนะนำสินค้าที่ใกล้เคียงได้อย่างมืออาชีพ
"""

def answer_question(user_message):
    context = search_faiss(user_message)

    # ✅ ถ้าไม่พบ context ให้หาสินค้าใกล้เคียงจาก keyword
    if not context:
        similar_context = search_faiss(user_message[:4])  # ลองหารหัส/ชื่อใกล้เคียง
        if similar_context:
            return f"ไม่พบสินค้าตรงกับ: '{user_message}'\nแต่เราแนะนำสินค้าใกล้เคียงดังนี้:\n{similar_context[:1000]}"
        else:
            return f"ขออภัยค่ะ ไม่พบข้อมูลสินค้าสำหรับ: '{user_message}'"

    # ✅ ตัด context ไม่ให้ยาวเกินไป
    context = context[:2000]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"ข้อมูลสินค้า:\n{context}\n\nคำถาม:\n{user_message}"}
        ],
        temperature=0.5,   # 👈 ปรับให้นุ่มนวลแต่ยังไม่หลุดหัวข้อ
        max_tokens=300     # 👈 จำกัดความยาวคำตอบ
    )

    return response.choices[0].message.content.strip()


