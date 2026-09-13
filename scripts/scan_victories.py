#!/usr/bin/env python3
"""Scan full rush for victory (green 'Vous avez gagné') and defeat (red) frames."""
import os, subprocess
import numpy as np
from PIL import Image

RUSH = "C:/Users/user/Desktop/Youtube jingle montage miniature/Montage/Rush video/2026-09-13 19-08-00.mp4"
BASE = os.path.expanduser("~/fliflight-mods/work/rush")
FR = f"{BASE}/dense"
os.makedirs(FR, exist_ok=True)

print("decoding (1 frame / 2s)...")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", RUSH,
                "-vf", "fps=1/2,scale=480:-2", "-q:v", "3", f"{FR}/f_%04d.jpg"], check=True)

frames = sorted(os.listdir(FR))
STEP = 2
rows = []
for i, fn in enumerate(frames):
    im = np.asarray(Image.open(f"{FR}/{fn}").convert("RGB")).astype(int)
    r, g, b = im[:, :, 0], im[:, :, 1], im[:, :, 2]
    # bright green text (victory): g high, r & b low
    green = int(((g > 170) & (r < 120) & (b < 120)).sum())
    # bright red text (defeat): r high, g & b low
    red = int(((r > 170) & (g < 120) & (b < 120)).sum())
    rows.append((i * STEP, green, red))

def top(rows, idx, label, n=40):
    s = sorted(rows, key=lambda x: x[idx], reverse=True)[:n]
    print(f"\n=== {label} ===")
    for t, gr, rd in sorted(s):
        print(f"  {t//60:02d}:{t%60:02d}  green={gr}  red={rd}")

top(rows, 1, "GREEN (victoire)", 40)
top(rows, 2, "RED (defaite)", 15)

# save full result
with open(f"{BASE}/scan_results.txt", "w") as f:
    for t, gr, rd in rows:
        f.write(f"{t}\t{gr}\t{rd}\n")
print("\nsaved scan_results.txt")
