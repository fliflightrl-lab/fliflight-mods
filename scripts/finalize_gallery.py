#!/usr/bin/env python3
"""Finalize the flagship gallery: 7 real CF screenshots + 2 assembled QoL images, clean names."""
import os, shutil
from PIL import Image

PK = r"C:\Users\user\fliflight-mods\packs\pvp-essentials"
SRC = os.path.join(PK, "gallery_src")
GAL = os.path.join(PK, "gallery")
QOL = os.path.join(SRC, "qol")
os.makedirs(QOL, exist_ok=True)

# 1. move the assembled QoL images (currently in gallery/) to gallery_src/qol/ before wiping
for fn in ["qol_pumpkin.png", "qol_lowfire.png"]:
    srcp = os.path.join(GAL, fn)
    if os.path.exists(srcp):
        shutil.move(srcp, os.path.join(QOL, fn))
        print(f"  moved {fn} -> gallery_src/qol/")

# 2. wipe + rebuild gallery
if os.path.isdir(GAL):
    shutil.rmtree(GAL)
os.makedirs(GAL, exist_ok=True)

order = [
    ("crosshair_0.png",      "01_crosshair.png"),
    ("crosshair_1.png",      "02_crosshair.png"),
    ("ores_0.png",           "03_visible_ores.png"),
    ("ores_1.png",           "04_visible_ores.png"),
    ("ores_2.png",           "05_visible_ores.png"),
    ("sword_0.jpg",          "06_short_sword.png"),
    ("sword_1.png",          "07_short_sword.png"),
    ("qol/qol_pumpkin.png",  "08_clear_pumpkin.png"),
    ("qol/qol_lowfire.png",  "09_low_fire.png"),
]

gallery_files = []
for src_name, dst_name in order:
    sp = os.path.join(SRC, src_name)
    dp = os.path.join(GAL, dst_name)
    if not os.path.exists(sp):
        print(f"  SKIP (missing): {src_name}")
        continue
    img = Image.open(sp).convert("RGB")
    img.save(dp, "PNG")
    gallery_files.append(dst_name)
    print(f"  {dst_name:24s} {os.path.getsize(dp):>8} bytes")

print(f"\n{len(gallery_files)} gallery images finalised")
print("ORDER:", gallery_files)
