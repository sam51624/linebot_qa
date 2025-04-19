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
                        "คุณคือระบบแยกประเภทคำถามลูกค้า (Intent Classification) สำหรับร้านคลองถมช้อปปิ้งมอลล์\n"
                        "ให้ตอบเพียง intent เดียวจากรายการนี้: product_inquiry, order_request, price_inquiry, general_question, "
                        "store_location, contact_info, delivery_info, payment_method, check_stock, unknown.\n"
                        "หากไม่แน่ใจให้ตอบว่า unknown เท่านั้น ห้ามตอบอย่างอื่น\n\n"
                        "ตัวอย่าง:\n"
                        "- 'รหัส 050127 ชื่ออะไร' → product_inquiry\n"
                        "- 'ชื่อสินค้าอะไร' → product_inquiry\n"
                        "- '050127 คืออะไร' → product_inquiry\n"
                        "- 'รหัสนี้มีของไหม' → check_stock\n"
                        "- 'ร้านอยู่ที่ไหน' → store_location\n"
                        "- 'มีบริการส่งของไหม' → delivery_info\n"
                        "- 'ชำระเงินยังไง' → payment_method\n"
                        "- 'เบอร์โทรร้านคืออะไร' → contact_info\n"
                        "- ถ้าไม่แน่ใจ ให้ตอบว่า unknown เท่านั้น"
                    )
                },
                {
                    "role": "user",
                    "content": f"ข้อความ: {user_message}"
                }
            ],
            temperature=0.3,
            max_tokens=30
        )

        intent = response.choices[0].message.content.strip()
        print("🎯 INTENT by GPT:", intent)
        return intent

    except Exception as e:
        print("❌ Error in detect_intent:", str(e))
        return "unknown"
