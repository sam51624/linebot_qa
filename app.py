from flask import Flask, request
from answer_question import answer_question
from data_logger import log_to_sheets
from intent_classifier import detect_intent
from ocr_utils import extract_info_from_image_bytes
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
        print("❌ Invalid payload")
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
                reply_text = "ขออภัยค่ะ ขณะนี้ยังไม่รองรับการสั่งซื้อผ่านไลน์ หากสนใจสามารถมาที่หน้าร้านคลองถมช้อปปิ้งมอลล์ได้เลยค่ะ"
            elif intent == "general_question":
                reply_text = "คุณสามารถติดต่อร้านคลองถมช้อปปิ้งมอลล์ ได้ที่หน้าร้าน หรือติดต่อผ่านเบอร์โทรที่ระบุไว้ในเพจค่ะ"
            elif intent == "store_location":
                reply_text = "ร้านคลองถมช้อปปิ้งมอลล์ ตั้งอยู่ที่ 'ถนนนวลจันทร์ ซอย17' ค่ะ ดูแผนที่: https://www.google.com/maps/place/คลองถมช้อปปิ้งมอลล์"
            elif intent == "contact_info":
                reply_text = (
                    "คุณสามารถติดต่อร้านคลองถมช้อปปิ้งมอลล์ ได้ทาง:
"
                    "- โทร: 02-1021772
- Line ID: @kts-mall
"
                    "- Email: klongthomshopping@gmail.com
- Facebook: https://www.facebook.com/ktsmall"
                )
            elif intent == "delivery_info":
                reply_text = (
                    "ร้านคลองถมช้อปปิ้งมอลล์ มีบริการจัดส่งทั่วประเทศผ่าน Kerry, Flash, ไปรษณีย์ไทย
"
                    "- ระยะเวลา 1–3 วันทำการ
"
                    "- ค่าจัดส่งตามน้ำหนัก/ขนาด
"
                    "- มีบริการเก็บเงินปลายทาง (COD) ได้ในวงเงินไม่เกิน 2000 บาทค่ะ"
                )
            elif intent == "payment_method":
                reply_text = (
                    "ร้านคลองถมช้อปปิ้งมอลล์ รับชำระเงินผ่าน:
"
                    "- โอนบัญชีธนาคาร
- พร้อมเพย์
- เงินสดหน้าร้าน
- บัตรเครดิต"
                )
            else:
                reply_text = "ขออภัยค่ะ ไม่เข้าใจคำถาม หากต้องการสอบถามสินค้า กรุณาระบุรหัสหรือชื่อสินค้าอีกครั้งนะคะ 😊"

            reply_text += f"

{qid}"
            send_reply(reply_token, reply_text)
            log_to_sheets(user_id, user_message, reply_text, intent)

        elif e["message"]["type"] == "image":
            message_id = e["message"]["id"]
            image_url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
            headers = {"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
            image_response = requests.get(image_url, headers=headers)

            if image_response.status_code == 200:
                send_reply(reply_token, "📷 รับภาพเรียบร้อยแล้ว กำลังโหลดข้อมูลสินค้า...")
                threading.Thread(target=process_image_async, args=(e,)).start()

    return "OK", 200

def process_image_async(event):
    try:
        user_id = event["source"]["userId"]
        message_id = event["message"]["id"]
        image_url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
        headers = {"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
        image_response = requests.get(image_url, headers=headers)

        if image_response.status_code != 200 or not image_response.content:
            push_message(user_id, "ไม่สามารถโหลดภาพได้ หรือภาพไม่มีข้อมูล 😢")
            return

        image_bytes = image_response.content
        extracted_info = extract_info_from_image_bytes(image_bytes)
        print("🧠 ข้อมูล OCR:", extracted_info)

        if not extracted_info:
            push_message(user_id, "ไม่พบข้อมูลรหัสหรือชื่อสินค้าจากภาพที่ส่งมาค่ะ")
            return

        responses = []
        for info in extracted_info:
            sku = info.get("sku")
            name = info.get("name")
            query = sku if sku else name
            ai_response = answer_question(query, user_id)
            if sku and name:
                responses.append(f"🔍 รหัส {sku} ({name}):
{ai_response}")
            elif sku:
                responses.append(f"🔍 รหัส {sku}:
{ai_response}")
            elif name:
                responses.append(f"🔍 สินค้า {name}:
{ai_response}")

        full_reply = "

".join(responses)
        push_message(user_id, full_reply)
        log_to_sheets(user_id, "[รูปภาพ]", full_reply, "image_ocr")

    except Exception as e:
        print("❌ Error in OCR thread:", e)
        push_message(user_id, "เกิดข้อผิดพลาดระหว่างการประมวลผลภาพค่ะ 😥")

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
        print("✅ LINE ตอบกลับ:", response.status_code)
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
