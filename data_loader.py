import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def load_data_from_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("ชื่อชีท").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)
