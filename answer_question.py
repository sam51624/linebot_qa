import openai
import os
from vector_store import search_faiss

openai.api_key = os.environ.get("OPENAI_API_KEY")

system_message = """
คุณคือพนักงานขายของร้านคลองถมช้อปปิ้งมอลล์
พูดจาสุภาพ กระชับ แนะนำสินค้าอย่างมืออาชีพ
เน้นว่าร้านมีของพร้อมส่ง ราคาถูก และซื้อได้ที่หน้าร้าน
หากลูกค้าไม่ตรงกับสินค้า ให้ตอบว่า 'ขออภัยค่ะ รบกวนสอบถามเพิ่มเติมได้นะคะ'
"""

def answer_question(user_message):
    # ดึงข้อมูลจาก vector store (หรือ Google Sheets ก็ได้)
    context = search_faiss(user_message)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # หรือ gpt-4 ถ้าคุณใช้เวอร์ชันนั้น
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"ข้อมูลสินค้า:\n{context}\n\nคำถาม:\n{user_message}"}
        ],
        temperature=0.7,
        max_tokens=500
    )

    return response["choices"][0]["message"]["content"].strip()

