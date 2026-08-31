"""Generate a 512x512 logo for the PvP HUD mod (programmatic render, no generative AI)."""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"C:\Users\user\fliflight-mods\dist\mod_gallery\pvphud-logo.png"
S = 512
BG = (16, 18, 26)

def font(sz):
    for name in ["arialbd.ttf", "arial.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(name, sz)
        except Exception:
            continue
    return ImageFont.load_default()

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)

# subtle radial glow behind
for r in range(180, 40, -12):
    alpha_shade = 12 + (180 - r) // 6
    d.ellipse([S/2 - r, S/2 - r, S/2 + r, S/2 + r], fill=(24 + alpha_shade, 28 + alpha_shade, 40 + alpha_shade))

# HUD panel (top-left corner style, centered)
px, py, pw, ph = 96, 118, 320, 216
d.rounded_rectangle([px, py, px+pw, py+ph], radius=16, fill=(10, 12, 18), outline=(80, 88, 112), width=3)

lines = [
    ("FPS", "144", (140, 255, 140)),
    ("PING", "23ms", (255, 220, 120)),
    ("XYZ", "124 64 -318", (130, 190, 255)),
    ("CPS", "12/9", (255, 130, 130)),
]
yy = py + 20
for name, val, col in lines:
    d.text((px + 20, yy), name, font=font(24), fill=(170, 175, 190))
    d.text((px + 200, yy), val, font=font(28), fill=col)
    if name != "CPS":
        d.line([(px + 20, yy + 42), (px + pw - 20, yy + 42)], fill=(44, 50, 68), width=2)
    yy += 44

# corner accents (PvP vibe)
accent = (255, 90, 90)
for (ax, ay, dx, dy) in [(18, 18, 46, 0), (S-18, 18, -46, 0), (18, S-18, 46, 0), (S-18, S-18, -46, 0)]:
    d.line([(ax, ay), (ax + dx, ay + dy)], fill=accent, width=5)

# title at bottom
d.text((S//2, S - 44), "PvP HUD", font=font(44), fill=(255, 255, 255), anchor="mm")

img.save(OUT)
print("saved", OUT)
