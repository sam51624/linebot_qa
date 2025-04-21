# 🔹 1. ใช้ Python base image แบบเล็ก
FROM python:3.10-slim

# 🔹 2. ตั้งค่าตัวแปรสิ่งแวดล้อม เพื่อให้เห็น log ทันที
ENV PYTHONUNBUFFERED=1

# 🔹 3. ติดตั้ง system dependencies ที่ vision API ต้องใช้
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 🔹 4. ตั้ง working directory
WORKDIR /app

# 🔹 5. คัดลอกไฟล์โปรเจกต์ทั้งหมด (สำคัญมากสำหรับให้ Cloud Build rebuild เสมอ)
COPY . .

# 🔹 6. ติดตั้ง Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 🔹 7. ตั้งค่าตำแหน่งของไฟล์ Service Account JSON ที่ Cloud Run mount เข้ามา
ENV GOOGLE_APPLICATION_CREDENTIALS="/etc/secrets/credentials.json"

# 🔹 8. Run ด้วย gunicorn และ bind ไปที่ $PORT (สำคัญกับ Cloud Run)
CMD ["gunicorn", "-b", "0.0.0.0:$PORT", "app:app"]

