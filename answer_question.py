import os
import google.generativeai as genai
from vector_store import search_faiss

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

system_message = """
คุณคือพนักงานขายของร้านคลองถมช้อปปิ้งมอลล์
พูดจาสุภาพ กระชับ แนะนำสินค้าอย่างมืออาชีพ
เน้นว่าร้านมีของพร้อมส่ง ราคาถูก และซื้อได้ที่หน้าร้าน
หากลูกค้าไม่ตรงกับสินค้า ให้ตอบว่า 'ขออภัยค่ะ รบกวนสอบถามเพิ่มเติมได้นะคะ'
"""

def answer_question(user_message):
    context = search_faiss(user_message)
    prompt = f"{system_message}\n\nข้อมูลสินค้า:\n{context}\n\nคำถาม:\n{user_message}"
    
    response = model.generate_content(prompt)
    return response.text.strip()
