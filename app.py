from flask import Flask, request
from answer_question import answer_question
from data_logger import log_to_sheets
from intent_classifier import detect_intent
from ocr_utils import extract_text_from_image

import requests
import os
from datetime import datetime
from hashlib import md5
import time

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
        if e["type"] != "message":
            continue

        user_id = e["source"]["userId"]
        reply_token = e["replyToken"]

        # === ✉️ ข้อความตัวอักษร
        if e["message"]["type"] == "text":
            user_message = e["message"]["text"]

        # เก็บประวัติการสนทนา
            if user_id not in chat_history:
                chat_history[user_id] = []
            chat_history[user_id].append(user_message)
            chat_history[user_id] = chat_history[user_id][-5:]

            # ตรวจจับ Intent
            intent = detect_intent(user_message)
            print("🎯 INTENT:", intent)

            # สร้าง QID สำหรับติดตาม
            qid = "#Q" + md5((user_id + user_message + str(time.time())).encode()).hexdigest()[:6]

            # ตอบตาม intent
            if intent == "product_inquiry":
                reply_text = answer_question(user_message, user_id)
            elif intent == "price_inquiry":
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
            elif intent == "check_stock":
                reply_text = answer_question(user_message, user_id)
            else:
                reply_text = "ขออภัยค่ะ ไม่เข้าใจคำถาม หากต้องการสอบถามสินค้า กรุณาระบุรหัสหรือชื่อสินค้าอีกครั้งนะคะ 😊"

            reply_text += f"\n\n{qid}"
            send_reply(reply_token, reply_text)
            log_to_sheets(user_id, user_message, reply_text, intent)

        # === 📸 กรณีเป็นภาพ
        elif e["message"]["type"] == "image":
            message_id = e["message"]["id"]
            image_url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
            headers = {"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
            image_response = requests.get(image_url, headers=headers)

            if image_response.status_code == 200:
                # ส่งภาพเข้า Google Cloud Vision OCR
                from google.cloud import vision
                client = vision.ImageAnnotatorClient()
                image = vision.Image(content=image_response.content)
                response = client.text_detection(image=image)
                texts = response.text_annotations

                if texts:
                    extracted_text = texts[0].description.strip()
                    print("🧠 OCR Text:", extracted_text)

                    # ตรวจจับ intent และตอบกลับอัตโนมัติ
                    intent = detect_intent(extracted_text)
                    reply_text = answer_question(extracted_text, user_id)
                    reply_text = f"จากข้อความในภาพ:\n\n{extracted_text}\n\n{reply_text}"
                else:
                    reply_text = "ไม่พบข้อความในภาพที่สามารถอ่านได้ค่ะ"

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
