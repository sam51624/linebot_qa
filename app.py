from flask import Flask, request, abort
from answer_question import answer_question
from data_logger import log_to_sheets
import requests
import os

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

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

@app.route("/webhook", methods=["POST"])
def webhook():
    event = request.get_json()

    if event is None or "events" not in event:
        return "Bad Request", 400

    for e in event["events"]:
        if e["type"] == "message" and e["message"]["type"] == "text":
            user_id = e["source"]["userId"]
            user_message = e["message"]["text"]
            reply_token = e["replyToken"]

            # ===== ใช้ AI ตอบลูกค้า =====
            reply_text = answer_question(user_message)

            # ===== ส่งข้อความกลับไปที่ LINE =====
            send_reply(reply_token, reply_text)

            # ===== บันทึก log คำถาม-คำตอบ =====
            log_to_sheets(user_id, user_message, reply_text)

    return "OK", 200
