from fastapi import FastAPI, WebSocket
import time

app = FastAPI(title="CNCai")

@app.get("/")
def root():
    return {"service": "CNCai", "ok": True}

@app.websocket("/ws/progress")
async def ws_progress(ws: WebSocket):
    await ws.accept()
    for i, step in enumerate(["preprocess","vectorize","toolpath","postprocess","pack"], start=1):
        await ws.send_json({"event": step, "progress": int(i*100/5)})
        time.sleep(0.5)
    await ws.close()
