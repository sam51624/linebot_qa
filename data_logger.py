import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def log_to_sheets(user_id, user_message, reply_text, intent):
    # 🔐 ใช้ credentials.json ที่อยู่ใน root folder
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # 👇 ชื่อ spreadsheet ต้องตรงกับที่คุณสร้างใน Google Drive
    sheet = client.open("log_conversations").sheet1  # เปลี่ยนชื่อถ้าคุณใช้ชื่ออื่น

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # บันทึกค่าทุกแถว
    sheet.append_row([now, user_id, user_message, reply_text, intent])
