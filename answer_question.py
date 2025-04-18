from vector_store import search_faiss

system_message = """
คุณคือพนักงานขายของร้านคลองถมช้อปปิ้งมอลล์ พูดจาสุภาพ กระชับ ให้ข้อมูลสินค้าอย่างชัดเจน
เน้นว่าร้านมีของพร้อมส่ง ราคาถูก และสามารถซื้อหน้าร้านได้ด้วย
หากลูกค้าถามไม่ตรงกับสินค้า ให้ตอบว่า 'ขออภัยค่ะ รบกวนสอบถามเพิ่มเติมได้นะคะ'
"""

def answer_question(query):
    context = search_faiss(query)
    return f"{system_message}\n\nข้อมูลสินค้า:\n{context}\n\nคำตอบ: ... (เรียก OpenAI ที่นี่)"
