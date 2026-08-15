#!/usr/bin/env python3
"""Regenerate the 'low fire' gallery image from the NEW compressed fire texture.

The old gallery image (09_low_fire.png) was built from the vanilla fire_0 strip,
which squashes the whole 16x512 animation band and looks buggy. This version shows
a single, clean, complete flame frame from the NEW compressed/lowered fire, upscaled
with NEAREST (pixel-art look) on a dark background, so the gallery reflects exactly
what the fixed pack delivers.
"""
import os
from PIL import Image

BASE = r"C:\Users\user\fliflight-mods"
NEW_FIRE = os.path.join(BASE, "build", "pvp-essentials", "assets", "minecraft",
                        "textures", "block", "fire_0.png")
OUT = os.path.join(BASE, "packs", "pvp-essentials", "gallery", "09_low_fire.png")

SIZE = 800
frame_px = int(SIZE * 0.62)          # on-screen size of the flame
bg = (10, 10, 12, 255)               # near-black, matches other gallery images

# Load the NEW compressed fire, take frame 0 (a complete lowered flame: tip + base)
img = Image.open(NEW_FIRE).convert("RGBA")
w, h = img.size
frame = img.crop((0, 0, w, w))       # first 16x16 frame

# Upscale with NEAREST to keep the crisp pixel-art look
flame = frame.resize((frame_px, frame_px), Image.NEAREST)

# Canvas
canvas = Image.new("RGBA", (SIZE, SIZE), bg)
fx = (SIZE - frame_px) // 2
fy = (SIZE - frame_px) // 2
canvas.paste(flame, (fx, fy), flame)

canvas.convert("RGB").save(OUT)
print(f"regenerated {OUT}  ({SIZE}x{SIZE}) from compressed fire frame 0")
print(f"  source flame size: {frame.size}, upscaled to {frame_px}x{frame_px}")
