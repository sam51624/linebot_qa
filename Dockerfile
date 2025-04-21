# 🔹 1. ใช้ Python image base
FROM python:3.10-slim

# 🔹 2. Set environment variable ปิด prompt
ENV PYTHONUNBUFFERED=1

# 🔹 3. ติดตั้ง dependencies ระบบที่จำเป็น (รวมถึง libglib ที่ vision ต้องใช้)
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 🔹 4. Create app directory
WORKDIR /app

# 🔹 5. Copy project files
COPY . /app

# 🔹 6. ติดตั้ง Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 🔹 7. ระบุ Path ไปยัง service account (ใน Cloud Run จะ mount ที่นี่)
ENV GOOGLE_APPLICATION_CREDENTIALS="/etc/secrets/credentials.json"

# 🔹 8. Run ด้วย gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
