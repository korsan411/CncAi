from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2, numpy as np, io, zipfile, base64
from settings import MACHINE_SETTINGS, POST_PROCESSORS
from utils.engine import make_toolpaths_cut, make_toolpaths_raster, multipass_zip_from_toolpaths
from utils.preview import extract_contours_and_heightmap

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

@app.websocket("/ws/progress")
async def ws_progress(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            # Expect JSON containing base64-encoded image and options
            data = await ws.receive_json()
            b64 = data.get("file_base64")
            if not b64:
                await ws.send_json({"event":"error","message":"No file_base64 provided"})
                continue
            try:
                img_bytes = base64.b64decode(b64)
                nparr = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            except Exception as e:
                await ws.send_json({"event":"error","message":f"Failed to decode image: {e}"})
                continue

            machine = data.get("machine","router")
            material = data.get("material","wood")
            mode = data.get("mode", "cut")
            try:
                total_depth = float(data.get("total_depth", 20.0))
                step_down = float(data.get("step_down", 5.0))
                tool_diameter = float(data.get("tool_diameter", 3.0))
                kerf = float(data.get("kerf", 0.15))
            except:
                await ws.send_json({"event":"error","message":"Invalid numeric parameters"})
                continue
            profile = data.get("profile", "grbl")

            config = MACHINE_SETTINGS.get(machine, {}).get(material)
            if not config:
                await ws.send_json({"event":"error","message":"Missing machine/material config"})
                continue
            pp = POST_PROCESSORS.get(profile, POST_PROCESSORS.get("grbl", {}))

            # 1) Toolpaths
            try:
                toolpaths = make_toolpaths_cut(img, machine=machine, tool_dia=tool_diameter, kerf=kerf) if mode=="cut"                             else make_toolpaths_raster(img)
            except Exception as e:
                await ws.send_json({"event":"error","message":f"Toolpath generation failed: {e}"})
                continue

            if not toolpaths:
                await ws.send_json({"event":"error","message":"No toolpaths generated - check the image or parameters"})
                continue

            # 2) ZIP passes and stream events
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                d = step_down; pass_idx = 1
                while d < total_depth:
                    await ws.send_json({"event":"pass_start","pass":pass_idx,"depth":d})
                    multipass_zip_from_toolpaths(zf, toolpaths, config, machine, d, step_down, pp, only_one=True, pass_idx=pass_idx)
                    await ws.send_json({"event":"pass_done","pass":pass_idx})
                    d += step_down; pass_idx += 1
                await ws.send_json({"event":"finishing","depth":total_depth+0.5})
                multipass_zip_from_toolpaths(zf, toolpaths, config, machine, total_depth, step_down, pp, finishing=True, pass_idx=pass_idx)

            zip_buffer.seek(0)
            await ws.send_bytes(zip_buffer.getvalue())
    except WebSocketDisconnect:
        pass
    except Exception:
        pass

@app.post("/analyze-image/")
async def analyze_image(file: UploadFile, depth: float = Form(2.0)):
    img_bytes = await file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    contours, heightmap_b64 = extract_contours_and_heightmap(img)
    return JSONResponse({"contours": contours, "heightmap": heightmap_b64, "depth": depth})
