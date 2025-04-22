from flask import Flask, request
from answer_question import answer_question
from data_logger import log_to_sheets
from intent_classifier import detect_intent
from ocr_utils import extract_info_from_image_bytes  # ← ฟังก์ชันใหม่
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

        threading.Thread(target=process_message_async, args=(e,)).start()

    return "OK", 200


def process_message_async(event):
    user_id = event["source"]["userId"]
    reply_token = event["replyToken"]
    msg_type = event["message"]["type"]

    if msg_type == "text":
        user_message = event["message"]["text"]
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

    elif msg_type == "image":
        message_id = event["message"]["id"]
        image_url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
        headers = {"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
        image_response = requests.get(image_url, headers=headers)

        if image_response.status_code == 200:
            send_reply(reply_token, "📷 รับภาพเรียบร้อยแล้ว กำลังตรวจสอบข้อมูลสินค้า...")

            image_bytes = image_response.content
            try:
                product_info_list = extract_info_from_image_bytes(image_bytes)

                print("🔍 ผลลัพธ์จาก OCR:", product_info_list)

                if product_info_list:
                    results = []
                    for info in product_info_list:
                        text_for_ai = info["sku"] if info["sku"] else info["name"]
                        ai_response = answer_question(text_for_ai, user_id)
                        response_text = f"🔍 รหัส: {info['sku'] or '-'}\nชื่อ: {info['name'] or '-'}\n\n{ai_response}"
                        results.append(response_text)
                    final_reply = "\n\n".join(results)
                else:
                    final_reply = "ไม่พบรหัสหรือชื่อสินค้าที่สามารถอ่านได้จากภาพค่ะ"

                push_message(user_id, final_reply)
                log_to_sheets(user_id, "[รูปภาพ]", final_reply, "image_ocr")

            except Exception as e:
                print("❌ OCR Error:", e)
                push_message(user_id, "เกิดข้อผิดพลาดระหว่างการประมวลผลรูปภาพค่ะ")


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
        print("✅ Reply status:", response.status_code)
        print("🔁 Response:", response.text)
    except Exception as e:
        print("❌ Reply Error:", e)


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
        print("📬 Push Response:", response.text)
    except Exception as e:
        print("❌ Push Error:", e)

