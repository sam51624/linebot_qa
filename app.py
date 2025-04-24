from flask import Flask, request
import json
import requests
from zort_api_utils import search_product_by_sku, format_product_reply
from ocr_utils import extract_text_from_image
from welcome_handler import is_greeting, generate_greeting_message

app = Flask(__name__)

# LINE API Credentials
LINE_CHANNEL_ACCESS_TOKEN = "qwzQAyLRTVcsHmcxBUvyrSojIDdxm4tO8Wl/LWEtfUARGP/ntFGSblJL/wM958SoBnyWRFtWK13Un6hcZxXk/BqM8H5FjjJpT40orkVVLJeoKCk6Aebsu8yPT4Yw+9lOV8ZWnklsQ5ueLSsIkNBCowdB04t89/1O/w1cDnyilFU="
LINE_REPLY_ENDPOINT = "https://api.line.me/v2/bot/message/reply"
LINE_CONTENT_ENDPOINT = "https://api-data.line.me/v2/bot/message/{}/content"

# In-memory set สำหรับจำว่า user คนไหนเคยได้รับข้อความทักทายแล้ว
GREETED_USERS = set()

def is_new_user(user_id: str) -> bool:
    return user_id not in GREETED_USERS

def mark_user_greeted(user_id: str):
    GREETED_USERS.add(user_id)

# ----------- Intent Classification -----------
def classify_intent(text: str) -> str:
    text = text.lower()
    if "ใบเสนอราคา" in text or "quote" in text or "เสนอราคา" in text:
        return "quotation"
    elif "มีของไหม" in text or "ของหมด" in text or "สต๊อก" in text:
        return "check_stock"
    else:
        return "search_product"

# ----------- ตอบกลับ LINE -----------
def reply_line(reply_token, message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post(LINE_REPLY_ENDPOINT, headers=headers, data=json.dumps(body))

# ----------- โหลดภาพจาก LINE -----------
def get_line_image(message_id):
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    url = LINE_CONTENT_ENDPOINT.format(message_id)
    response = requests.get(url, headers=headers)
    return response.content

# ----------- Webhook หลัก -----------
@app.route("/webhook", methods=["POST"])
def webhook():
    event_data = request.json
    for event in event_data.get("events", []):
        if event["type"] == "message":
            reply_token = event["replyToken"]

            # --- ข้อความ (Text)
            if event["message"]["type"] == "text":
                user_text = event["message"]["text"].strip()
                user_id = event["source"].get("userId")

                # ✅ เช็คว่าทักทาย และยังไม่เคยตอบ
                if is_greeting(user_text) and user_id and is_new_user(user_id):
                    message = generate_greeting_message()
                    reply_line(reply_token, message)
                    mark_user_greeted(user_id)
                    return "OK", 200

                intent = classify_intent(user_text)

                if intent == "search_product":
                    product = search_product_by_sku(user_text)
                    message = format_product_reply(product) if product else "ขออภัยค่ะ ไม่พบข้อมูลสินค้าที่คุณสอบถามมาเลยค่ะ 🙏"

                elif intent == "check_stock":
                    product = search_product_by_sku(user_text)
                    if product:
                        stock = product.get("quantity", "ไม่ระบุ")
                        message = f"🔎 รหัส: {product['code']}\n📦 สินค้า: {product['name']}\n📊 คงเหลือ: {stock} ชิ้น"
                    else:
                        message = "ไม่พบข้อมูลสินค้าที่จะตรวจสอบคงเหลือค่ะ"

                elif intent == "quotation":
                    message = "📄 หากคุณต้องการใบเสนอราคา กรุณาระบุรหัสสินค้าและจำนวน แล้วเราจะจัดทำให้โดยเร็วค่ะ 🙏"

                reply_line(reply_token, message)

            # --- รูปภาพ (Image)
            elif event["message"]["type"] == "image":
                image_id = event["message"]["id"]
                image_bytes = get_line_image(image_id)
                results = extract_text_from_image(image_bytes)

                if results:
                    sku = results[0].get("sku")
                    name = results[0].get("name")
                    intent = "search_product"

                    if sku:
                        product = search_product_by_sku(sku)
                        if product:
                            message = format_product_reply(product)
                        else:
                            message = f"🚫 ระบบยังไม่สามารถเชื่อมต่อข้อมูลจาก Zort ได้ในขณะนี้ หรือไม่พบรหัส {sku} ค่ะ"

                    elif name:
                        message = f"ระบบตรวจพบชื่อสินค้า: {name} \nแต่ยังไม่มีรหัสสินค้า กรุณาส่งรหัสอีกครั้งค่ะ 🙏"

                    else:
                        message = "ขออภัยค่ะ ระบบไม่สามารถอ่านข้อมูลจากภาพได้ค่ะ 😥"
                else:
                    message = "ไม่สามารถดึงข้อมูลจากภาพได้เลยค่ะ 😔"

                reply_line(reply_token, message)

    return "OK", 200

