#!/usr/bin/env python3
"""Analyze flame orientation: where are the opaque pixels in each frame of fire_0.png?"""
from PIL import Image

for name in ["fire_0.png", "fire_1.png"]:
    img = Image.open(rf"C:\Users\user\fliflight-mods\packs\pvp-essentials\vanilla_src\{name}").convert("RGBA")
    w, h = img.size
    n = h // w  # number of 16x16 frames
    print(f"\n=== {name} {w}x{h} ({n} frames) ===")
    for fidx in [0, 8, 16, 24]:
        # frame is a w x w block starting at y = fidx*w
        box = img.crop((0, fidx * w, w, (fidx + 1) * w))
        px = box.load()
        # count opaque-ish pixels per row (top=0..15)
        rows = []
        for y in range(w):
            cnt = sum(1 for x in range(w) if px[x, y][3] > 30)
            rows.append(cnt)
        # show top half vs bottom half totals
        top = sum(rows[:8])
        bot = sum(rows[8:])
        print(f"  frame {fidx:2d}: top-half opaque={top:3d}  bottom-half opaque={bot:3d}  (rows={rows})")
