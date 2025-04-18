from flask import Flask, request, abort
from answer_question import answer_question
from data_logger import log_to_sheets

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    event = request.get_json()

    if event is None or "events" not in event:
        return "Bad Request", 400

    for e in event["events"]:
        if e["type"] == "message" and e["message"]["type"] == "text":
            user_id = e["source"]["userId"]
            user_message = e["message"]["text"]

            # ===== ตอบกลับลูกค้าด้วย AI หรือข้อความอื่น ๆ =====
            reply_text = "ขอบคุณที่ติดต่อมานะคะ ทางร้านจะรีบตอบกลับค่ะ"

            # ส่งข้อความกลับไปหา LINE
            reply_token = e["replyToken"]
            send_reply(reply_token, reply_text)

    return "OK", 200

