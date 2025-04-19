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
                        "product_inquiry, order_request, price_inquiry, general_question, unknown. อย่าตอบอย่างอื่น"
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
        intent_examples = {
    "product_inquiry": [
        "มีรหัสสินค้า", "มีสินค้า", "มีสายไฟ", "มอเตอร์", "บอร์ด"
    ],
    "price_inquiry": [
        "ราคาเท่าไหร่", "แพงไหม", "กี่บาท"
    ],
    "order_request": [
        "สั่งซื้อได้ไหม", "ส่งของไหม", "ซื้อได้ไหม"
    ],
    "general_question": [
        "เปิดกี่โมง", "เบอร์โทร", "ชื่อร้าน", "ติดต่อ"
    ],
    "store_location": [
        "ร้านอยู่ที่ไหน", "ขอแผนที่", "ไปยังไง", "แผนที่ร้าน", "พิกัดร้าน"
    ]
}



