import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def test_logging():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("log_conversations").sheet1

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, "test_user", "ข้อความทดสอบ", "ตอบกลับทดสอบ", "test_intent"])

    print("✅ เขียนข้อมูลลง Google Sheet สำเร็จ!")

test_logging()
