# ========= Build frontend =========
FROM node:18 AS frontend-build
WORKDIR /app/frontend
COPY frontend/ /app/frontend/
RUN npm install && npm run build

# ========= Backend =========
FROM python:3.10-slim
WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend source
COPY backend/ /app/backend/

# Copy frontend build into backend static
COPY --from=frontend-build /app/frontend/dist /app/backend/static

WORKDIR /app/backend
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
