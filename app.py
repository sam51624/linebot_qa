from flask import Flask, request, abort
from answer_question import answer_question
from data_logger import log_to_sheets

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    event = request.get_json()
    try:
        user_id = event["events"][0]["source"]["userId"]
        message = event["events"][0]["message"]["text"]
    except:
        return abort(400)

    answer = answer_question(message)
    log_to_sheets(user_id, message, answer)
    return "OK"
