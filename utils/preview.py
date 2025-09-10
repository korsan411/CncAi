"""
utils/preview.py
Utilities for image enhancement and preview:
- generate_preview_base64(path): returns a small PNG encoded as base64
- image_to_heightmap(path): returns a 2D numpy array normalized 0-255
"""
import cv2
import numpy as np
import base64
import io
from PIL import Image
import tempfile

def generate_preview_base64(path, max_size=600):
    img = cv2.imread(path)
    if img is None:
        raise ValueError("Cannot read image for preview.")
    # resize for preview
    h,w = img.shape[:2]
    scale = min(1.0, max_size / max(h,w))
    nh = int(h*scale)
    nw = int(w*scale)
    img_small = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)
    # optional denoise
    img_small = cv2.fastNlMeansDenoisingColored(img_small, None, 10,10,7,21)
    # convert to PNG bytes
    img_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(img_rgb)
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    b = buf.getvalue()
    return base64.b64encode(b).decode("ascii")

def image_to_heightmap(path, target_size=256):
    """
    Convert image to grayscale and resize to (target_size, target_size).
    Return numpy uint8 array 0-255 where 0 -> low, 255 -> high.
    """
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Cannot read image for heightmap.")
    # denoise
    img = cv2.fastNlMeansDenoising(img, None, 10,7,21)
    # normalize and resize
    h0,w0 = img.shape[:2]
    # maintain aspect by padding to square
    size = max(h0,w0)
    top = (size - h0)//2
    left = (size - w0)//2
    padded = 255 * np.ones((size,size), dtype=np.uint8)
    padded[top:top+h0, left:left+w0] = img
    resized = cv2.resize(padded, (target_size, target_size), interpolation=cv2.INTER_AREA)
    # invert so darker -> deeper (optional)
    resized = cv2.normalize(resized, None, 0, 255, cv2.NORM_MINMAX)
    return resized
