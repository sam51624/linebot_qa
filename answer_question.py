from openai import OpenAI
import os
from vector_store import search_faiss

# สร้าง client ด้วย API Key จาก Environment
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

system_message = """
คุณคือพนักงานขายของร้านคลองถมช้อปปิ้งมอลล์...
"""

def answer_question(user_message):
    context = search_faiss(user_message)

    # ✅ พิมพ์ API Key (แค่บางส่วน) เพื่อ debug
    print("✅ OPENAI_API_KEY = ", api_key[:8], "***")

    # เรียก OpenAI
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"ข้อมูลสินค้า:\n{context}\n\nคำถาม:\n{user_message}"}
        ],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()

