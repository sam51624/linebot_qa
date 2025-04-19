def detect_intent(user_message):
    message = user_message.lower()

    if any(word in message for word in ["มีไหม", "มีมั้ย", "มีมั้ยคะ", "เหลือไหม", "เหลือมั้ย", "สินค้า", "รหัส"]):
        return "product_inquiry"

    if "ราคา" in message:
        return "price_inquiry"

    if any(word in message for word in ["สั่งซื้อ", "สั่งได้ไหม", "สั่งทางนี้ได้มั้ย", "ซื้อได้ไหม", "สั่งทางนี้ได้มั้ย"]):
        return "order_request"

    if any(word in message for word in ["เปิด", "ปิด", "ติดต่อ", "เบอร์", "เวลา", "ที่อยู่", "แผนที่"]):
        return "general_question"

    return "unknown"
