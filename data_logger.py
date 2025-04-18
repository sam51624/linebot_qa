import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def log_to_sheets(user_id, question, answer):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("LINE AI Logs").sheet1
    sheet.append_row([datetime.now().isoformat(), user_id, question, answer])
