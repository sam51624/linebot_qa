from flask import Flask, request
from answer_question import answer_question
from data_logger import log_to_sheets
from intent_classifier import detect_intent
from ocr_utils import extract_sku_from_bytes
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

# เก็บประวัติการสนทนา
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
                    "คุณสามารถติดต่อร้านคลองถมช้อปปิ้งมอลล์ ได้ทาง:\n"
                    "- โทร: 02-1021772\n- Line ID: @kts-mall\n"
                    "- Email: klongthomshopping@gmail.com\n- Facebook: https://www.facebook.com/ktsmall"
                )
            elif intent == "delivery_info":
                reply_text = (
                    "ร้านคลองถมช้อปปิ้งมอลล์ มีบริการจัดส่งทั่วประเทศผ่าน Kerry, Flash, ไปรษณีย์ไทย\n"
                    "- ระยะเวลา 1–3 วันทำการ\n"
                    "- ค่าจัดส่งตามน้ำหนัก/ขนาด\n"
                    "- มีบริการเก็บเงินปลายทาง (COD) ได้ในวงเงินไม่เกิน 2000 บาทค่ะ"
                )
            elif intent == "payment_method":
                reply_text = (
                    "ร้านคลองถมช้อปปิ้งมอลล์ รับชำระเงินผ่าน:\n"
                    "- โอนบัญชีธนาคาร\n- พร้อมเพย์\n- เงินสดหน้าร้าน\n- บัตรเครดิต"
                )
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
                        sku_list = extract_sku_from_bytes(image_bytes)
                        print(f"🔍 SKU ที่ตรวจพบ: {sku_list}")

                        if sku_list:
                            responses = []
                            for sku in sku_list:
                                ai_response = answer_question(sku, user_id)
                                responses.append(f"🔍 รหัส {sku}:\n{ai_response}")
                            full_reply = "\n\n".join(responses)
                        else:
                            full_reply = "ไม่พบรหัสสินค้าที่สามารถอ่านได้จากภาพค่ะ"

                        push_message(user_id, full_reply)
                        log_to_sheets(user_id, "[รูปภาพ]", full_reply, "image_ocr")

                    except Exception as e:
                        print("❌ Error in OCR thread:", e)

                threading.Thread(target=process_image_async).start()

    return "OK", 200


def send_reply(reply_token, message):
    print("📤 กำลังส่งข้อความกลับไปที่ LINE:")
    print("↪️ reply_token:", reply_token)
    print("📦 message:", message)

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
        print("🔁 LINE response text:", response.text)
    except Exception as e:
        print("❌ Error sending LINE reply:", e)


def push_message(user_id, message):
    print("📨 Push message to", user_id)
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
        print("📬 Push Response:", response.text)
    except Exception as e:
        print("❌ Error sending push:", e)
