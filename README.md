# CNCai

مشروع ويب لتحويل الصور إلى G-code يدعم 2D و 3D ويدعم عدة ماكينات (Router, Laser, Plasma).

## التشغيل محليًا
### Backend
```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```
### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Docker
```bash
docker compose up --build
```

## Railway
اربط المشروع من GitHub وسينشئ خدمتين (backend & frontend) تلقائيًا.

---
English section:

## CNCai
Web project to convert images into G-code (2D/3D) for CNC machines (Router, Laser, Plasma).
