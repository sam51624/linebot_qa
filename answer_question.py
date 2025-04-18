from openai import OpenAI
import os
from vector_store import search_faiss

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

system_message = """
คุณคือพนักงานขายของร้านคลองถมช้อปปิ้งมอลล์...
"""

def answer_question(user_message):
    context = search_faiss(user_message)

    # ✅ ตัด context ไม่ให้ยาวเกินไป
    context = context[:2000]

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

