#!/usr/bin/env python3
"""Build timestamped contact sheets from sampled frames."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.expanduser("~/fliflight-mods/work/rush")
FR = f"{BASE}/frames"
SH = f"{BASE}/sheets"
os.makedirs(SH, exist_ok=True)

STEP = 20  # seconds between frames
COLS, ROWS = 5, 5
TW, TH = 480, 270
LABEL_H = 34
FONT = r"C:\Windows\Fonts\arialbd.ttf"

frames = sorted(os.listdir(FR))
def ts(i):  # frame index (0-based) -> timestamp label
    s = i * STEP
    return f"{s//60:02d}:{s%60:02d}"

per_sheet = COLS * ROWS
n_sheets = (len(frames) + per_sheet - 1) // per_sheet
font = ImageFont.truetype(FONT, 26)

for s in range(n_sheets):
    chunk = frames[s*per_sheet:(s+1)*per_sheet]
    W = COLS * TW
    H = ROWS * (TH + LABEL_H)
    sheet = Image.new("RGB", (W, H), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for k, fn in enumerate(chunk):
        gi = s*per_sheet + k
        r, c = divmod(k, COLS)
        x = c * TW
        y = r * (TH + LABEL_H)
        im = Image.open(f"{FR}/{fn}").convert("RGB").resize((TW, TH))
        sheet.paste(im, (x, y))
        d.rectangle((x, y+TH, x+TW, y+TH+LABEL_H), fill=(0, 0, 0))
        d.text((x+8, y+TH+4), f"#{gi+1}  {ts(gi)}", font=font, fill=(255, 220, 60))
    out = f"{SH}/sheet_{s+1:02d}.png"
    sheet.save(out)
    print(out, sheet.size, f"frames {s*per_sheet+1}-{s*per_sheet+len(chunk)}")
print("TOTAL sheets:", n_sheets)
