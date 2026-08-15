#!/usr/bin/env python3
"""Assemble the two QoL gallery images: item on black + red 'barrier' no-sign overlay.

- pumpkin.png  : pumpkin item, red no-sign on top  -> 'clear pumpkin' (effect disabled)
- lowfire.png  : fire texture, red no-sign on top  -> 'low fire' (effect disabled)
"""
import os
from PIL import Image, ImageDraw, ImageFont

V = r"C:\Users\user\fliflight-mods\packs\pvp-essentials\gallery_src\vanilla"
OUT = r"C:\Users\user\fliflight-mods\packs\pvp-essentials\gallery"

def load(name):
    return Image.open(os.path.join(V, name)).convert("RGBA")

def assemble(item_name, out_name, size=800):
    canvas = Image.new("RGBA", (size, size), (10, 10, 12, 255))  # near-black bg

    # item centered, scaled up with NEAREST (pixel-art look)
    item = load(item_name)
    item_px = int(size * 0.52)
    item = item.resize((item_px, item_px), Image.NEAREST)
    ix = (size - item_px) // 2
    iy = (size - item_px) // 2
    canvas.paste(item, (ix, iy), item)

    # barrier no-sign overlay, larger, centered on top
    barrier = load("barrier.png")
    bar_px = int(size * 0.58)
    barrier = barrier.resize((bar_px, bar_px), Image.NEAREST)
    bx = (size - bar_px) // 2
    by = (size - bar_px) // 2
    canvas.paste(barrier, (bx, by), barrier)

    path = os.path.join(OUT, out_name)
    canvas.convert("RGB").save(path)
    print(f"  {out_name:20s} {size}x{size} <- {item_name} + barrier overlay")

os.makedirs(OUT, exist_ok=True)
assemble("pumpkin_side.png", "qol_pumpkin.png")
assemble("fire_0.png", "qol_lowfire.png")
print("done")
