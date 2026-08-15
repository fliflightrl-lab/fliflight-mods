#!/usr/bin/env python3
"""Investigate crosshair + fire paths/content in the 1.21.4 jar and the flagship pack."""
import os, zipfile, io
from PIL import Image

JAR = r"C:\Users\user\fliflight-mods\build\client-1.21.4.jar"
PK_ZIP = r"C:\Users\user\fliflight-mods\packs\pvp-essentials\files\pvp-essentials-1.0.1-resourcepack-1.21.4.zip"

print("=" * 60)
print("1) CROSSHAIR files in the 1.21.4 jar")
print("=" * 60)
with zipfile.ZipFile(JAR) as z:
    for n in sorted(z.namelist()):
        if "crosshair" in n.lower():
            print(f"  {n}")

print("\n" + "=" * 60)
print("2) FIRE files (ALL paths) in the jar")
print("=" * 60)
with zipfile.ZipFile(JAR) as z:
    for n in sorted(z.namelist()):
        if "fire" in n.lower() and n.endswith((".png", ".mcmeta", ".json")):
            print(f"  {n}")

print("\n" + "=" * 60)
print("3) CROSSHAIR content in the flagship pack")
print("=" * 60)
with zipfile.ZipFile(PK_ZIP) as z:
    names = z.namelist()
    ch = [n for n in names if "crosshair" in n.lower()]
    print(f"  crosshair files in pack: {ch}")
    for c in ch:
        data = z.read(c)
        img = Image.open(io.BytesIO(data)).convert("RGBA")
        px = img.load()
        opaque = sum(1 for y in range(img.size[1]) for x in range(img.size[0]) if px[x, y][3] > 30)
        print(f"  {c}: {img.size}  opaque_pixels={opaque}  bytes={len(data)}")

print("\n" + "=" * 60)
print("4) FIRE content in the flagship pack")
print("=" * 60)
with zipfile.ZipFile(PK_ZIP) as z:
    for fn in ["assets/minecraft/textures/block/fire_0.png",
               "assets/minecraft/textures/block/fire_1.png"]:
        if fn in z.namelist():
            data = z.read(fn)
            img = Image.open(io.BytesIO(data)).convert("RGBA")
            print(f"  {fn}: {img.size} bytes={len(data)}")
        else:
            print(f"  {fn}: MISSING")

print("\n" + "=" * 60)
print("5) User screenshots (basic analysis)")
print("=" * 60)
for p in [r"C:\Users\user\AppData\Roaming\Hermes\composer-images\composer_2026-08-15_01-26-32-626_dcfad7.png",
          r"C:\Users\user\AppData\Roaming\Hermes\composer-images\composer_2026-08-15_01-26-45-565_f4c696.png",
          r"C:\Users\user\AppData\Roaming\Hermes\composer-images\composer_2026-08-15_01-26-54-793_e51616.png"]:
    if os.path.exists(p):
        img = Image.open(p).convert("RGB")
        # sample: center pixel (crosshair area), bottom band (fire area)
        w, h = img.size
        center = img.getpixel((w // 2, h // 2))
        # bottom 20% average
        band = img.crop((0, int(h * 0.8), w, h))
        band_small = band.resize((1, 1))
        bottom = band_small.getpixel((0, 0))
        print(f"  {os.path.basename(p)}: {w}x{h} center={center} bottom_avg={bottom}")
    else:
        print(f"  MISSING: {p}")
