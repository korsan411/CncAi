import cv2, numpy as np
from shapely.geometry import Polygon, LinearRing
from shapely.ops import unary_union
import zipfile

SCALE = 0.1  # px -> mm

def _img_to_contours(img):
    _, th = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return contours

def _contour_to_poly(cnt):
    pts = [(float(x)*SCALE, float(y)*SCALE) for [[x,y]] in cnt]
    if len(pts) < 3: return None
    ring = LinearRing(pts)
    if not ring.is_ccw:
        pts = list(reversed(pts))
    try:
        return Polygon(pts)
    except Exception:
        return None

def make_toolpaths_cut(img, machine="router", tool_dia=3.0, kerf=0.15):
    contours = _img_to_contours(img)
    polys = [p for c in contours if (p:=_contour_to_poly(c)) and p.is_valid]
    if not polys: return []
    union = unary_union(polys)
    if machine == "router":
        offset = -(tool_dia/2.0)
    elif machine in ("laser","plasma"):
        offset = -(kerf/2.0)
    else:
        offset = 0.0
    def offset_geom(g):
        try:
            return g.buffer(offset, join_style=2, resolution=2)
        except Exception:
            return None
    off = offset_geom(union) if offset != 0 else union
    if off is None: off = union
    toolpaths = []
    if off.geom_type == "Polygon" or off.geom_type == 'LinearRing':
        toolpaths.append(list(off.exterior.coords))
    elif off.geom_type == "MultiPolygon":
        for poly in off.geoms:
            toolpaths.append(list(poly.exterior.coords))
    else:
        for p in polys:
            toolpaths.append(list(p.exterior.coords))
    return toolpaths

def make_toolpaths_raster(img, step=0.5):
    h, w = img.shape
    _, th = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    toolpaths = []
    step_px = max(1, int(step / SCALE))
    for y in range(0, h, step_px):
        line = []
        for x in range(w):
            if th[y, x] > 0:
                line.append((x*SCALE, y*SCALE))
        if line:
            toolpaths.append(line)
    return toolpaths

def _emit_header(pp, machine, config, feed):
    hdr = pp.get("start",[])[:]
    if machine == "router":
        if callable(pp.get("spindle_on")):
            hdr += pp["spindle_on"](config)
    elif machine == "laser" and callable(pp.get("laser_on")):
        hdr += pp["laser_on"](config)
    elif callable(pp.get("plasma_on")):
        hdr += pp["plasma_on"](config)
    hdr += [f"F{feed}"]
    return hdr

def _toolpaths_to_gcode(toolpaths, machine, config, depth, pp):
    g = _emit_header(pp, machine, config, config.get("feed",600))
    g.append("G0 Z5")
    for path in toolpaths:
        if not path: continue
        x0,y0 = path[0]
        g.append(f"G0 X{round(x0,3)} Y{round(y0,3)} Z5")
        g.append(f"G1 Z-{round(depth,3)} F300")
        for (x,y) in path[1:]:
            g.append(f"G1 X{round(x,3)} Y{round(y,3)}")
        g.append("G0 Z5")
    g += pp.get("stop",[])
    return "\n".join(g)

def multipass_zip_from_toolpaths(zf, toolpaths, config, machine, depth, step_down, pp, only_one=False, finishing=False, pass_idx=1):
    g = _toolpaths_to_gcode(toolpaths, machine, config, depth if not finishing else (depth+0.5), pp)
    name = f"finishing_pass_{pass_idx}.nc" if finishing else f"pass_{pass_idx}_{round(depth,2)}.nc"
    zf.writestr(name, g)
    return g
