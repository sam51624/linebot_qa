import openai
import os

# ดึง API Key จาก Environment Variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def detect_intent(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "คุณคือระบบแยกประเภทคำถามลูกค้า (Intent Classification) สำหรับร้านคลองถมช้อปปิ้งมอลล์ ให้ตอบเพียง intent เดียวจากรายการนี้เท่านั้น: product_inquiry, order_request, price_inquiry, general_question, unknown. อย่าตอบอย่างอื่น"
                },
                {
                    "role": "user",
                    "content": f"ข้อความ: {user_message}"
                }
            ],
            temperature=0.0  # คงที่เพื่อให้ผลลัพธ์แม่นยำเสมอ
        )

        intent = response.choices[0].message.content.strip()
        print("🎯 INTENT by GPT:", intent)
        return intent

    except Exception as e:
        print("❌ Error in detect_intent:", str(e))
        return "unknown"

