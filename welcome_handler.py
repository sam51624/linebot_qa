from datetime import datetime

def is_greeting(text: str) -> bool:
    greetings = ["สวัสดี", "hello", "hi", "ทักทาย", "สวัสดีค่ะ", "สวัสดีครับ"]
    return any(greet in text.lower() for greet in greetings)

def generate_greeting_message() -> str:
    hour = datetime.now().hour
    greeting = "สวัสดีตอนเช้าค่ะ" if hour < 12 else "สวัสดีตอนบ่ายค่ะ"
    return f"""{greeting}
ดิฉันคือแอดมิน AI พร้อมให้บริการข้อมูลเบื้องต้นค่ะ
คุณสามารถส่งรหัสสินค้า หรือรูปภาพสินค้ามาให้ตรวจสอบได้นะคะ"""

# ✅ เพิ่ม memory set สำหรับจำ user ที่เคยทักทายแล้ว
GREETED_USERS = set()

def is_new_user(user_id: str) -> bool:
    return user_id not in GREETED_USERS

def mark_user_greeted(user_id: str):
    GREETED_USERS.add(user_id)
