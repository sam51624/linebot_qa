from flask import Flask, request
from answer_question import answer_question
from data_logger import log_to_sheets
from intent_classifier import detect_intent
from ocr_utils import extract_info_from_image_bytes  # ← ใช้ฟังก์ชันใหม่นี้
import requests
import os
import threading
from hashlib import md5
import time
import json

app = Flask(__name__)
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

if not LINE_CHANNEL_ACCESS_TOKEN:
    raise Exception("❌ LINE_CHANNEL_ACCESS_TOKEN ไม่ถูกตั้งค่าใน Environment Variable")

chat_history = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    print("🚀 Webhook Triggered")
    event = request.get_json()
    print("📥 Event payload:", json.dumps(event, indent=2, ensure_ascii=False))

    if event is None or "events" not in event:
        return "Bad Request", 400

    for e in event["events"]:
        if e["type"] != "message":
            continue

        user_id = e["source"]["userId"]
        reply_token = e["replyToken"]

        if e["message"]["type"] == "text":
            user_message = e["message"]["text"]
            print(f"📩 Text from {user_id}: {user_message}")

            if user_id not in chat_history:
                chat_history[user_id] = []
            chat_history[user_id].append(user_message)
            chat_history[user_id] = chat_history[user_id][-5:]

            intent = detect_intent(user_message)
            print("🎯 INTENT:", intent)

            qid = "#Q" + md5((user_id + user_message + str(time.time())).encode()).hexdigest()[:6]

            if intent in ["product_inquiry", "price_inquiry", "check_stock"]:
                reply_text = answer_question(user_message, user_id)
            elif intent == "order_request":
                reply_text = "ขออภัยค่ะ ขณะนี้ยังไม่รองรับการสั่งซื้อผ่านไลน์..."
            elif intent == "general_question":
                reply_text = "คุณสามารถติดต่อร้านคลองถมช้อปปิ้งมอลล์ ได้ที่หน้าร้าน..."
            elif intent == "store_location":
                reply_text = "ร้านคลองถมช้อปปิ้งมอลล์ ตั้งอยู่ที่ 'ถนนนวลจันทร์ ซอย17'..."
            elif intent == "contact_info":
                reply_text = (
                    "คุณสามารถติดต่อร้านคลองถมช้อปปิ้งมอลล์ ได้ทาง:\n"
                    "- โทร: 02-1021772\n- Line ID: @kts-mall\n"
                    "- Email: klongthomshopping@gmail.com"
                )
            elif intent == "delivery_info":
                reply_text = "มีบริการจัดส่งทั่วประเทศผ่าน Kerry, Flash, ไปรษณีย์ไทย..."
            elif intent == "payment_method":
                reply_text = "รับชำระเงินผ่าน: โอน/พร้อมเพย์/เงินสด/บัตรเครดิต"
            else:
                reply_text = "ขออภัยค่ะ ไม่เข้าใจคำถาม หากต้องการสอบถามสินค้า กรุณาระบุรหัสหรือชื่อสินค้าอีกครั้งนะคะ 😊"

            reply_text += f"\n\n{qid}"
            send_reply(reply_token, reply_text)
            log_to_sheets(user_id, user_message, reply_text, intent)

        elif e["message"]["type"] == "image":
            message_id = e["message"]["id"]
            image_url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
            headers = {"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
            image_response = requests.get(image_url, headers=headers)

            if image_response.status_code == 200:
                print(f"🖼 รับภาพจาก {user_id} แล้ว เริ่ม OCR ด้วย Thread...")
                send_reply(reply_token, "📷 รับภาพเรียบร้อยแล้ว กำลังตรวจสอบข้อมูลสินค้า...")

                def process_image_async():
                    try:
                        image_bytes = image_response.content
                        extracted = extract_info_from_image_bytes(image_bytes)
                        print("🔍 Extracted OCR info:", extracted)

                        if not extracted:
                            push_message(user_id, "ไม่สามารถอ่านรหัสหรือชื่อสินค้าจากภาพได้ค่ะ")
                            return

                        responses = []
                        for item in extracted:
                            query_text = item["sku"] or item["name"]
                            if not query_text:
                                continue
                            answer = answer_question(query_text, user_id)
                            part = "🔍 "
                            if item["sku"]:
                                part += f"รหัส {item['sku']}"
                            if item["name"]:
                                part += f" | {item['name']}"
                            part += f"\n{answer}"
                            responses.append(part)

                        full_reply = "\n\n".join(responses)
                        push_message(user_id, full_reply)
                        log_to_sheets(user_id, "[รูปภาพ]", full_reply, "image_ocr")

                    except Exception as e:
                        print("❌ Error in OCR thread:", e)

       # ตอบ LINE กลับทันที           
       threading.Thread(target=process_image_async, args=(event,)).start()
       return "OK", 200

def send_reply(reply_token, message):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        print("✅ LINE ตอบกลับ status code:", response.status_code)
    except Exception as e:
        print("❌ Error sending LINE reply:", e)

def push_message(user_id, message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        print("📬 Push Status:", response.status_code)
    except Exception as e:
        print("❌ Error sending push:", e)

