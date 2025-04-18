from flask import Flask, request, abort
from answer_question import answer_question
from data_logger import log_to_sheets

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    event = request.get_json()

    if event is None:
        return "Bad Request", 400

    # ทดสอบให้ตอบกลับ 200 ไปก่อน
    return "OK", 200
