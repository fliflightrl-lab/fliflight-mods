#!/usr/bin/env python3
"""Compare flagship crosshair vs original; detailed screenshot analysis."""
import os, zipfile, io
from PIL import Image

FLAG_ZIP = r"C:\Users\user\fliflight-mods\packs\pvp-essentials\files\pvp-essentials-1.0.1-resourcepack-1.21.4.zip"
DOT_ZIP = r"C:\Users\user\fliflight-mods\packs\dot-crosshair-cossx-better-crosshair\files\best_crosshair-1.0.0-resourcepack-1.21.4.zip"
CH = "assets/minecraft/textures/gui/sprites/hud/crosshair.png"

# 1. byte-for-byte compare
with zipfile.ZipFile(FLAG_ZIP) as zf, zipfile.ZipFile(DOT_ZIP) as zd:
    f_data = zf.read(CH)
    d_data = zd.read(CH)
    print("1) crosshair.png flagship vs original dot pack:")
    print(f"   flagship: {len(f_data)} bytes")
    print(f"   original: {len(d_data)} bytes")
    print(f"   IDENTICAL: {f_data == d_data}")
    # pixel detail
    img = Image.open(io.BytesIO(d_data)).convert("RGBA")
    px = img.load()
    print(f"   size: {img.size}")
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if px[x, y][3] > 30:
                print(f"   opaque pixel at ({x},{y}) color={px[x, y]}")

# 2. screenshot analysis
print("\n2) Screenshots — crosshair dot + fire detection:")
shots = [
    r"C:\Users\user\AppData\Roaming\Hermes\composer-images\composer_2026-08-15_01-26-32-626_dcfad7.png",
    r"C:\Users\user\AppData\Roaming\Hermes\composer-images\composer_2026-08-15_01-26-45-565_f4c696.png",
    r"C:\Users\user\AppData\Roaming\Hermes\composer-images\composer_2026-08-15_01-26-54-793_e51616.png",
]
for p in shots:
    if not os.path.exists(p):
        continue
    img = Image.open(p).convert("RGB")
    w, h = img.size
    px = img.load()
    # crosshair: search 80x80 around center for bright (near-white) pixels
    cx, cy = w // 2, h // 2
    bright = 0
    for y in range(cy - 40, cy + 40):
        for x in range(cx - 40, cx + 40):
            r, g, b = px[x, y]
            if r > 200 and g > 200 and b > 200:
                bright += 1
    # fire: search bottom 25% for orange/red (fire-ish)
    fire = 0
    for y in range(int(h * 0.75), h):
        for x in range(0, w, 3):  # sample
            r, g, b = px[x, y]
            if r > 150 and g > 40 and g < 160 and b < 90:  # orange/red
                fire += 1
    print(f"   {os.path.basename(p)[:40]}: bright_center={bright} fire_orange={fire}")
