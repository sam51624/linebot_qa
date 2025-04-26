### ✅ app.py

[เนื้อหาไฟล์ app.py ตามเดิม]


### ✅ product_api.py

[เนื้อหาไฟล์ product_api.py ตามเดิม]


### 📄 README.md

# KTS LINE AI BOT + Cloud Run API + PostgreSQL

ระบบ AI LINE Bot สำหรับตอบแชทอัตโนมัติ + REST API สำหรับจัดการสินค้า
เชื่อมต่อ LINE Official Account, Google Cloud Run, PostgreSQL และ OCR ด้วย Python (Flask)

---

## 🔧 โครงสร้างโปรเจกต์

```
linebot_qa/
│
├── app.py                  # Webhook LINE + ลงทะเบียน blueprint
├── product_api.py          # REST API: GET/POST สินค้า
├── db_config.py            # การเชื่อมต่อ Cloud SQL (PostgreSQL)
├── db_models.py            # โครงสร้างตาราง: Product, Order, Customer ฯลฯ
├── db_utils.py             # ฟังก์ชันค้นหาสินค้าจากฐานข้อมูล (SKU)
├── ocr_utils.py            # OCR ด้วย Google Cloud Vision API
├── welcome_handler.py      # ฟังก์ชันทักทายผู้ใช้ใหม่ใน LINE
├── Dockerfile              # สำหรับ Deploy ขึ้น Cloud Run
├── requirements.txt        # รายการ Python packages
└── README.md               # คู่มือใช้งาน
```

---

## 🧠 ฟีเจอร์หลัก

| ฟีเจอร์                            | รายละเอียด |
|-----------------------------------|-------------|
| ✅ LINE Webhook                   | ตอบข้อความและภาพจากลูกค้าโดยอัตโนมัติ |
| 🧾 Intent Classification           | วิเคราะห์ข้อความเป็นหมวด: `quotation`, `check_stock`, `search_product` |
| 🔍 OCR (Google Cloud Vision)       | อ่านรหัสสินค้า/ชื่อสินค้าจากภาพ |
| 📦 REST API `/products`            | รองรับ `GET` และ `POST` เพื่อดึงและเพิ่มสินค้า |
| ☁️ Cloud SQL (PostgreSQL)          | เก็บข้อมูลสินค้า ลูกค้า ออเดอร์ ฯลฯ |
| 🔑 OAuth Google API                | สำหรับเชื่อม Google Sheet และ Google Cloud Vision |

---

## 🚀 วิธี Deploy บน Cloud Run

1. **เตรียม Service Account Key JSON**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
   ```

2. **Build Docker Image**
   ```bash
   docker build -t gcr.io/[PROJECT-ID]/linebot-qa .
   ```

3. **Deploy**
   ```bash
   gcloud run deploy kts-line-ai \
     --image gcr.io/[PROJECT-ID]/linebot-qa \
     --platform managed \
     --region asia-southeast1 \
     --allow-unauthenticated \
     --add-cloudsql-instances [INSTANCE_CONNECTION_NAME] \
     --set-env-vars GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/credentials.json
   ```

4. **ตั้งค่า LINE Webhook**
   - URL: `https://<your-cloudrun-url>/webhook`

---

## 🛠 POST /products (เพิ่มสินค้า)

```json
POST /products
Content-Type: application/json

{
  "sku": "MOTOR001",
  "name": "มอเตอร์เกียร์ 12V",
  "description": "มอเตอร์เกียร์ขนาดเล็ก ใช้งานทั่วไป",
  "category": "มอเตอร์",
  "cost_price": 100.00,
  "price": 180.00,
  "stock_quantity": 10,
  "available_stock": 10,
  "image_url": "https://example.com/motor.jpg"
}
```

---

## ✅ ตัวอย่าง Response จาก /products

```json
[
  {
    "sku": "MOTOR001",
    "name": "มอเตอร์เกียร์ 12V",
    "price": 180.00,
    "stock_quantity": 10
  }
]
```

---

## ✨ ติดตั้งไลบรารีที่ใช้

```bash
pip install -r requirements.txt
```

---

## 📬 ติดต่อผู้พัฒนา

> LINE: @yourlineid  
> GitHub: github.com/yourname  
> Cloud Run URL: [https://kts-line-ai-xxxxxxxxxx.run.app](#)
