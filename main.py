from fastapi import FastAPI, File, UploadFile, WebSocket, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import base64
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from utils import preview
from utils import engine
import tempfile
import os

app = FastAPI(title="CNC Image -> Gcode Service (MVP)")

executor = ThreadPoolExecutor(max_workers=2)

@app.post("/analyze-image/")
async def analyze_image(file: UploadFile = File(...), mode: str = "2d"):
    """
    Simple endpoint: accepts an image and returns a small JSON with a base64 preview (PNG)
    and a job id for generating outputs. For MVP we process synchronously but offload heavy
    work to a thread executor to avoid blocking the event loop.
    """
    content = await file.read()
    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix)
    tmp.write(content)
    tmp.flush()
    tmp.close()

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(executor, process_image_sync, tmp.name, mode)

    # Clean up temp file
    try:
        os.unlink(tmp.name)
    except Exception:
        pass

    return JSONResponse(result)

def process_image_sync(path, mode):
    """
    Runs in thread executor. Returns dict with preview (base64 PNG) and filenames of generated artifacts.
    """
    try:
        # Preprocess + preview
        preview_png_b64 = preview.generate_preview_base64(path)
        # For 2D: extract contours -> generate toolpaths -> gcode
        if mode == "2d":
            contours = engine.img_to_contours(path)
            toolpaths = engine.make_toolpaths_from_contours(contours)
            gcode = engine.toolpaths_to_gcode(toolpaths)
            artifacts = {"gcode": gcode}
        else:
            # 3D flow: create heightmap (numpy) -> stl -> basic gcode (raster)
            heightmap = preview.image_to_heightmap(path)
            stl_path = engine.heightmap_to_stl(heightmap)
            # simplest: return stl filename (contents)
            artifacts = {"stl_path": stl_path}
        return {"status": "ok", "preview_base64": preview_png_b64, "artifacts": artifacts}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.websocket("/ws/progress")
async def websocket_progress(ws: WebSocket):
    await ws.accept()
    # For MVP we just send heartbeat/progress demo messages
    try:
        for i in range(0, 101, 10):
            await ws.send_json({"progress": i})
            await asyncio.sleep(0.2)
        await ws.send_json({"progress": 100, "status": "done"})
    finally:
        await ws.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
