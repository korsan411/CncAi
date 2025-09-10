import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

# ✅ تقديم واجهة React كملفات ثابتة
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/health")
def health():
    return {"service": "CNCai", "ok": True}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
