# ========= Build frontend =========
FROM node:18 AS frontend-build
WORKDIR /app/frontend
COPY frontend/ /app/frontend/
RUN npm install && npm run build

# ========= Backend =========
FROM python:3.10-slim
WORKDIR /app

# تثبيت المتطلبات
COPY backend/ /app/backend/
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# نسخ الـ frontend المبني إلى backend
COPY --from=frontend-build /app/frontend/dist /app/backend/static

# تشغيل FastAPI (مع خدمة الملفات الثابتة للواجهة)
WORKDIR /app/backend
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
