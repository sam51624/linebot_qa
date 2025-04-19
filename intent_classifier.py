import openai
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def detect_intent(user_message):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "คุณคือระบบแยกประเภทคำถามลูกค้า (Intent Classification) สำหรับร้านคลองถมช้อปปิ้งมอลล์ "
                        "ให้ตอบเพียง intent เดียวจากรายการนี้เท่านั้น: "
                        "product_inquiry, order_request, price_inquiry, general_question, store_location, contact_info, delivery_info, unknown. "
                        "หากไม่แน่ใจให้ตอบว่า unknown เท่านั้น ห้ามตอบอย่างอื่น"
                    )
                },
                {
                    "role": "user",
                    "content": f"ข้อความ: {user_message}"
                }
            ],
            temperature=0.0
        )

        intent = response.choices[0].message.content.strip()
        print("🎯 INTENT by GPT:", intent)
        return intent

    except Exception as e:
        print("❌ Error in detect_intent:", str(e))
        return "unknown"
