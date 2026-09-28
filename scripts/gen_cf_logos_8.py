"""Generate 512x512 CurseForge project logos for the 8 new packs (CF requires >= 400x400)."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = r"C:\Users\user\fliflight-mods"
PACKS = os.path.join(BASE, "packs")
OUT = os.path.join(BASE, "dist", "cf_logos")
os.makedirs(OUT, exist_ok=True)

SLUGS = [
    "fliflight-low-shield",
    "fliflight-no-vignette",
    "fliflight-clear-water",
    "fliflight-clear-lava",
    "fliflight-clear-spyglass",
    "fliflight-clean-hotbar",
    "fliflight-thin-totem",
    "fliflight-clear-powder-snow",
]

def font(sz):
    for n in ["arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"]:
        try:
            return ImageFont.truetype(n, sz)
        except Exception:
            continue
    return ImageFont.load_default()

for slug in SLUGS:
    src = os.path.join(PACKS, slug, "icon.png")
    icon = Image.open(src).convert("RGBA")
    S = 512
    canvas = Image.new("RGBA", (S, S), (14, 14, 18, 255))
    # subtle vignette-ish glow
    d = ImageDraw.Draw(canvas)
    for r in range(230, 60, -10):
        a = 8 + int((230 - r) / 5)
        d.ellipse([S/2 - r, S/2 - r, S/2 + r, S/2 + r], fill=(20 + a, 24 + a, 34 + a, 255))
    # paste the icon art scaled to fit a 320px box (keeps pixel-art look)
    box = 320
    w, h = icon.size
    scale = min(box / w, box / h)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    art = icon.resize((nw, nh), Image.NEAREST)
    canvas.paste(art, ((S - nw) // 2, (S - nh) // 2 - 20), art)
    # label
    label = slug.replace("fliflight-", "").replace("-", " ").upper()
    f = font(40)
    tb = d.textbbox((0, 0), label, font=f)
    d.text(((S - (tb[2] - tb[0])) // 2, S - 90), label, fill=(235, 235, 242, 255), font=f)
    out = os.path.join(OUT, slug + "-512.png")
    canvas.convert("RGB").save(out)
    print(f"  {slug}-512.png  ({os.path.getsize(out)} bytes)")

print("DONE ->", OUT)
