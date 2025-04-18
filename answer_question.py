import os
import google.generativeai as genai
from vector_store import search_faiss

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/chat-bison-001")

system_message = """
คุณคือพนักงานขายของร้านคลองถมช้อปปิ้งมอลล์...
"""

def answer_question(user_message):
    context = search_faiss(user_message)
    prompt = f"{system_message}\n\nข้อมูลสินค้า:\n{context}\n\nคำถาม:\n{user_message}"

    response = model.generate_content(prompt)
    return response.text.strip()
