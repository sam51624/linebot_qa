from flask import Flask, request
from answer_question import answer_question
from data_logger import log_to_sheets
from intent_classifier import detect_intent
from ocr_utils import extract_text_from_image

import requests
import os
import time
from datetime import datetime
from hashlib import md5

app = Flask(__name__)
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

# เก็บประวัติการสนทนา
chat_history = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    event = request.get_json()

    if event is None or "events" not in event:
        return "Bad Request", 400

    for e in event["events"]:
        user_id = e["source"]["userId"]
        reply_token = e["replyToken"]

        # กรณีข้อความเป็น text
        if e["type"] == "message" and e["message"]["type"] == "text":
            user_message = e["message"]["text"]

            # เก็บประวัติการสนทนา
            if user_id not in chat_history:
                chat_history[user_id] = []
            chat_history[user_id].append(user_message)
            chat_history[user_id] = chat_history[user_id][-5:]

            # ตรวจจับ Intent
            intent = detect_intent(user_message)
            print("🎯 INTENT:", intent)

            # สร้าง QID
            qid = "#Q" + md5((user_id + user_message + str(time.time())).encode()).hexdigest()[:6]

            if intent in ["product_inquiry", "price_inquiry", "check_stock"]:
                reply_text = answer_question(user_message, user_id)

            elif intent == "order_request":
                reply_text = "ขออภัยค่ะ ขณะนี้ยังไม่รองรับการสั่งซื้อผ่านไลน์ หากสนใจสามารถมาที่หน้าร้านคลองถมช้อปปิ้งมอลล์ได้เลยค่ะ"

            elif intent == "general_question":
                reply_text = "คุณสามารถติดต่อร้านคลองถมช้อปปิ้งมอลล์ ได้ที่หน้าร้าน หรือติดต่อผ่านเบอร์โทรที่ระบุไว้ในเพจค่ะ"

            elif intent == "store_location":
                reply_text = "ร้านคลองถมช้อปปิ้งมอลล์ ตั้งอยู่ที่ 'ถนนนวลจันทร์ ซอย17' ค่ะ สามารถกดดูแผนที่ได้ที่นี่: https://www.google.com/maps/place/คลองถมช้อปปิ้งมอลล์"

            elif intent == "contact_info":
                reply_text = (
                    "คุณสามารถติดต่อร้านคลองถมช้อปปิ้งมอลล์ ได้ทาง:\n"
                    "- โทร: 02-1021772\n"
                    "- Line ID: @kts-mall\n"
                    "- Email: klongthomshopping@gmail.com\n"
                    "- Facebook: https://www.facebook.com/ktsmall\n"
                    "- หรือมาที่หน้าร้าน คลองถมช้อปปิ้งมอลล์ (ถนนนวลจันทร์ ซอย17)"
                )

            elif intent == "delivery_info":
                reply_text = (
                    "ร้านคลองถมช้อปปิ้งมอลล์ มีบริการจัดส่งสินค้าทั่วประเทศผ่านขนส่งเอกชน เช่น Kerry, Flash, ไปรษณีย์ไทย\n"
                    "- ระยะเวลาจัดส่ง: 1–3 วันทำการ (ขึ้นอยู่กับพื้นที่)\n"
                    "- ค่าจัดส่งขึ้นอยู่กับขนาดและน้ำหนักสินค้า\n"
                    "- ทางเรามีบริการเก็บเงินปลายทางในยอดไม่เกิน 2000 บาท โดยไปรษณีย์ไทย\n"
                    "- หากต้องการสั่งซื้อ กรุณาสอบถามสินค้ากับแอดมินก่อนค่ะ"
                )

            elif intent == "payment_method":
                reply_text = (
                    "ร้านคลองถมช้อปปิ้งมอลล์ รับชำระเงินผ่าน:\n"
                    "- โอนบัญชีธนาคาร (แจ้งเลขบัญชีเมื่อสรุปคำสั่งซื้อ)\n"
                    "- พร้อมเพย์\n"
                    "- เงินสดหน้าร้าน\n"
                    "- บัตรเครดิต\n"
                    "หากต้องการชำระเงิน กรุณาติดต่อแอดมินเพื่อยืนยันรายการค่ะ"
                )

            else:
                reply_text = "ขออภัยค่ะ ไม่เข้าใจคำถาม หากต้องการสอบถามสินค้า กรุณาระบุรหัสหรือชื่อสินค้าอีกครั้งนะคะ 😊"

            reply_text += f"\n\n{qid}"
            send_reply(reply_token, reply_text)
            log_to_sheets(user_id, user_message, reply_text, intent)

        # กรณีข้อความเป็นภาพ
        elif e["type"] == "message" and e["message"]["type"] == "image":
            message_id = e["message"]["id"]
            image_url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
            headers = {"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
            image_data = requests.get(image_url, headers=headers).content

            # วิเคราะห์ OCR
            extracted_text = extract_text_from_image(image_data)
            print("🧾 OCR Text:", extracted_text)

            if extracted_text:
                reply_text = answer_question(extracted_text, user_id)
            else:
                reply_text = "ขออภัยค่ะ ไม่สามารถอ่านข้อความจากภาพได้ค่ะ"

            qid = "#Q" + md5((user_id + str(time.time())).encode()).hexdigest()[:6]
            reply_text += f"\n\n{qid}"

            send_reply(reply_token, reply_text)
            log_to_sheets(user_id, "[รูปภาพ]", reply_text, "image_ocr")

    return "OK", 200


def send_reply(reply_token, message):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    requests.post(url, headers=headers, json=payload)
