from openai import OpenAI
import os
from vector_store import search_faiss  # ดึง context จากเวกเตอร์หรือฐานข้อมูล
# หากคุณยังไม่ใช้ vector store สามารถเปลี่ยน search_faiss เป็นฟังก์ชันที่คืน string ก็ได้

# เตรียม client สำหรับเรียก OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Prompt สำหรับ ChatGPT
system_message = """
คุณคือพนักงานขายของร้านคลองถมช้อปปิ้งมอลล์
พูดจาสุภาพ กระชับ แนะนำสินค้าอย่างมืออาชีพ
เน้นว่าร้านมีของพร้อมส่ง ราคาถูก และซื้อได้ที่หน้าร้าน
หากลูกค้าไม่ตรงกับสินค้า ให้ตอบว่า 'ขออภัยค่ะ รบกวนสอบถามเพิ่มเติมได้นะคะ'
"""

def answer_question(user_message):
    # ดึงข้อมูล context จาก vector store หรือข้อมูลที่เกี่ยวข้อง
    context = search_faiss(user_message)

    # เรียก ChatGPT พร้อม context
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # หรือ "gpt-4"
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"ข้อมูลสินค้า:\n{context}\n\nคำถาม:\n{user_message}"}
        ],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()
