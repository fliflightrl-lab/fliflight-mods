#!/usr/bin/env python3
"""Inspect the dot + bigger-dot crosshair packs to understand the target dot size."""
import zipfile, io
from PIL import Image

packs = {
    "dot":       r"C:\Users\user\fliflight-mods\packs\dot-crosshair-cossx-better-crosshair\files\best_crosshair-1.0.0-resourcepack-1.21.4.zip",
    "bigger-dot": r"C:\Users\user\fliflight-mods\packs\bigger-dot-crosshair-cossx-better-crosshair\files\dot_crosshair-1.0.0-resourcepack-1.21.4.zip",
}
CH = "assets/minecraft/textures/gui/sprites/hud/crosshair.png"

for name, path in packs.items():
    with zipfile.ZipFile(path) as z:
        img = Image.open(io.BytesIO(z.read(CH))).convert("RGBA")
        px = img.load()
        w, h = img.size
        # find opaque pixel bounding box + count
        xs, ys = [], []
        for y in range(h):
            for x in range(w):
                if px[x, y][3] > 30:
                    xs.append(x); ys.append(y)
        if xs:
            print(f"{name}: {w}x{h}, {len(xs)} opaque px, bbox x=[{min(xs)}..{max(xs)}] y=[{min(ys)}..{max(ys)}]")
        else:
            print(f"{name}: {w}x{h}, EMPTY")
