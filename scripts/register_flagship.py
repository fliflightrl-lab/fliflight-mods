#!/usr/bin/env python3
"""Register the flagship pack in the pipeline: copy file + icon, generate gallery banner."""
import os, shutil
from PIL import Image, ImageDraw, ImageFont

BASE = r"C:\Users\user\fliflight-mods"
PK   = os.path.join(BASE, "packs", "pvp-essentials")

os.makedirs(os.path.join(PK, "files"), exist_ok=True)
os.makedirs(os.path.join(PK, "gallery"), exist_ok=True)

# 1. copy the built zip into files/
src = os.path.join(BASE, "dist", "pvp-essentials-1.0.0-resourcepack-1.21.4.zip")
dst = os.path.join(PK, "files", "pvp-essentials-1.0.0-resourcepack-1.21.4.zip")
shutil.copy2(src, dst)
print("copied zip ->", dst)

# 2. icon = the generated pack.png
icon_src = os.path.join(BASE, "build", "pvp-essentials", "pack.png")
icon_dst = os.path.join(PK, "icon.png")
shutil.copy2(icon_src, icon_dst)
print("copied icon ->", icon_dst)

# 3. gallery banner (illustrative, 16:9 = 1280x720)
W, H = 1280, 720
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)], fill=(int(12 + t * 10), int(14 + t * 12), int(22 + t * 24), 255))

ACCENT = (0, 220, 180, 255)

def feature(x, title, sub):
    # icon dot
    d.ellipse([x - 10, 90 - 10, x + 10, 90 + 10], fill=ACCENT)
    d.text((x + 20, 82), title, fill=(255, 255, 255, 255))
    d.text((x + 20, 112), sub, fill=(180, 180, 190, 255))

# title
d.text((W // 2 - 260, 40), "PvP Essentials", fill=(255, 255, 255, 255))
d.text((W // 2 - 260, 140), "Crosshair  +  Visible Ores  +  Short Sword  +  Low Fire", fill=ACCENT)

feature(160, "Better crosshair", "clean dot, high visibility")
feature(160, "Visible ores", "see every ore through shaders")  # will overwrite y — do proper layout
# proper three-row layout
y0 = 280
for i, (t, s) in enumerate([
    ("Better crosshair", "clean dot, high visibility (24k+ downloads)"),
    ("Visible ores", "every ore stands out, shader-ready (13k+)"),
    ("Short sword", "smaller swords for better PvP view (5k+)"),
    ("Low fire + clear pumpkin", "nothing blocks your vision"),
]):
    yy = y0 + i * 90
    d.ellipse([160 - 14, yy + 8 - 14, 160 + 14, yy + 8 + 14], fill=ACCENT)
    d.text((190, yy), t, fill=(255, 255, 255, 255))
    d.text((190, yy + 32), s, fill=(170, 175, 185, 255))

gallery = os.path.join(PK, "gallery", "gallery_0.png")
img.convert("RGB").save(gallery)
print("generated gallery ->", gallery, os.path.getsize(gallery), "bytes")
