import os
from fastapi import FastAPI, UploadFile, File, Form, WebSocket
from fastapi.staticfiles import StaticFiles
import uvicorn, io, zipfile, time

app = FastAPI(title="AICNC")

# Serve React frontend from static directory
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/health")
def health():
    return {"service":"AICNC","ok":True}

@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...), machine: str = Form("router")):
    return {"filename": file.filename, "machine": machine, "status": "analyzed"}

@app.websocket("/ws/progress")
async def ws_progress(ws: WebSocket):
    await ws.accept()
    params = await ws.receive_json()
    steps = [("preprocess","تحميل الصورة"),("vectorize","تحليل الحواف"),("toolpath","توليد المسارات"),("finalize","الإخراج")]
    for i,(k,label) in enumerate(steps, start=1):
        await ws.send_json({"event":k,"label":label,"progress":int(i*100/len(steps))})
        time.sleep(0.6)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("output.nc","G0 X0 Y0\nM30\n")
        z.writestr("README.txt","Placeholder output from AICNC")
    await ws.send_bytes(buf.getvalue())
    await ws.close()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
