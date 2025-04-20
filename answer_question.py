from search_products import search_products
from vector_store import search_faiss
from openai import OpenAI
import os

chat_history = {}
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

system_message = """
คุณคือพนักงานขายของร้านคลองถมช้อปปิ้งมอลล์ ให้ข้อมูลสินค้า ตอบคำถามลูกค้า และแนะนำสินค้าที่ใกล้เคียงได้อย่างมืออาชีพ
"""

def normalize_text(text):
    return text.strip().replace(" ", "").replace("-", "").lower()

def answer_question(user_message, user_id=None):
    cleaned_message = normalize_text(user_message)

    # ✅ ค้นหาโดยตรงจาก Google Sheet
    result = search_products(cleaned_message)
    if "ไม่พบข้อมูลสินค้า" not in result:
        return result

    # ✅ หากไม่เจอ → ค้นหาแบบ vector ด้วย FAISS
    context = search_faiss(cleaned_message)
    if context:
        context = context[:2000]
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"ข้อมูลสินค้า:\n{context}\n\nคำถาม:\n{user_message}"}
        ]

        if user_id:
            user_chat = chat_history.get(user_id, [])[-3:]
            for m in user_chat:
                messages.insert(-1, m)
            chat_history.setdefault(user_id, []).append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.5,
            max_tokens=300
        )

        reply = response.choices[0].message.content.strip()

        if user_id:
            chat_history[user_id].append({"role": "assistant", "content": reply})

        return f"🔍 ไม่พบข้อมูลตรงจากระบบสินค้า แต่พบรายการใกล้เคียง:\n\n{reply}"

    return "ขออภัยค่ะ ไม่พบข้อมูลสินค้าที่คุณสอบถามมาเลยค่ะ 🙏"


