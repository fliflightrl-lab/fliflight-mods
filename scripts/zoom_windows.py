#!/usr/bin/env python3
"""Extract fine (1/3s) frames for candidate highlight windows + build per-window sheets."""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.expanduser("~/fliflight-mods/work/rush")
SRC = "C:/Users/user/Desktop/Youtube jingle montage miniature/Montage/Rush video/2026-09-13 19-08-00.mp4"
OUT = f"{BASE}/zoom"
os.makedirs(OUT, exist_ok=True)

# windows: (name, start_s, dur_s)
WINDOWS = [
    ("A_victoire_0300", 90, 100),     # 01:30 -> 03:10
    ("B_victoire_1920", 1070, 100),   # 17:50 -> 19:30
    ("C_victoire_4200", 2430, 100),   # 40:30 -> 42:10
    ("D_victoire_5140", 3010, 100),   # 50:10 -> 51:50
    ("E_fight_7200", 4280, 100),      # 71:20 -> 73:00
]

STEP = 3
FONT = r"C:\Windows\Fonts\arialbd.ttf"
font = ImageFont.truetype(FONT, 24)
TW, TH, LH = 384, 216, 30
COLS = 5

for name, start, dur in WINDOWS:
    d = f"{OUT}/{name}"
    os.makedirs(d, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-t", str(dur),
                    "-i", SRC, "-vf", f"fps=1/{STEP},scale={TW}:-2", "-q:v", "4", f"{d}/f_%03d.jpg"],
                   check=True)
    frames = sorted(os.listdir(d))
    frames = [f for f in frames if f.endswith(".jpg")]
    # build sheet
    rows = (len(frames) + COLS - 1) // COLS
    W = COLS * TW
    H = rows * (TH + LH)
    sheet = Image.new("RGB", (W, H), (20, 20, 20))
    dr = ImageDraw.Draw(sheet)
    for k, fn in enumerate(frames):
        t = start + k * STEP
        r, c = divmod(k, COLS)
        x, y = c * TW, r * (TH + LH)
        im = Image.open(f"{d}/{fn}").convert("RGB").resize((TW, TH))
        sheet.paste(im, (x, y))
        dr.rectangle((x, y+TH, x+TW, y+TH+LH), fill=(0, 0, 0))
        dr.text((x+6, y+TH+3), f"{t//60:02d}:{t%60:02d}", font=font, fill=(255, 220, 60))
    sp = f"{OUT}/{name}.png"
    sheet.save(sp)
    print(sp, f"{len(frames)} frames, {rows} rows, times {start//60:02d}:{start%60:02d}..{(start+dur)//60:02d}:{(start+dur)%60:02d}")
