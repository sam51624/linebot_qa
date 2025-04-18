import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def load_data_from_sheet():
    # กำหนด scope สำหรับ Google Sheets + Drive API
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # อ่าน credentials จากไฟล์ JSON
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # เปิด Google Sheet ตามชื่อที่ตั้งไว้
    sheet = client.open("สินค้าร้านคลองถม").sheet1  # เปลี่ยนชื่อถ้าไม่ตรง

    # ใช้แถวที่ 2 เป็น header
    data = sheet.get_all_records(head=2)

    # แปลงเป็น DataFrame
    df = pd.DataFrame(data)
    return df
