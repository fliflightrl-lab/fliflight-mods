#!/usr/bin/env python3
"""Generate a portfolio of example custom crosshairs (PIL) + a composed grid sheet.

Output: portfolio/*.png (individual examples) + portfolio/portfolio-sheet.jpg.
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "portfolio")
os.makedirs(OUT, exist_ok=True)

BG = (20, 20, 28, 255)
WHITE = (240, 240, 245, 255)
RED = (255, 72, 72, 255)
BLUE = (80, 160, 255, 255)
GREEN = (90, 220, 140, 255)


def cross_with_gap(d, c, length, gap, width, color):
    hw = width // 2
    d.rectangle([c - hw, c - length, c + hw, c - gap], fill=color)
    d.rectangle([c - hw, c + gap, c + hw, c + length], fill=color)
    d.rectangle([c - length, c - hw, c - gap, c + hw], fill=color)
    d.rectangle([c + gap, c - hw, c + length, c + hw], fill=color)


def render(fn, size=256, bg=BG):
    S = size * 4
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fn(d, S // 2)
    img = img.resize((size, size), Image.LANCZOS)
    b = Image.new("RGBA", (size, size), bg)
    b.alpha_composite(img)
    return b


def dot(color):
    def f(d, c):
        r = 90
        d.ellipse([c - r, c - r, c + r, c + r], fill=color)
    return f


def classic(color=WHITE):
    def f(d, c):
        cross_with_gap(d, c, 240, 60, 56, color)
    return f


def sniper(color=GREEN):
    def f(d, c):
        cross_with_gap(d, c, 300, 90, 28, color)
        d.ellipse([c - 26, c - 26, c + 26, c + 26], fill=color)
        for pos in (-300, 300):
            d.rectangle([c - 40, c + pos - 10, c + 40, c + pos + 10], fill=color)
            d.rectangle([c + pos - 10, c - 40, c + pos + 10, c + 40], fill=color)
    return f


def circle_dot(color=WHITE):
    def f(d, c):
        d.ellipse([c - 150, c - 150, c + 150, c + 150], outline=color, width=20)
        d.ellipse([c - 48, c - 48, c + 48, c + 48], fill=color)
    return f


def diamond_center(color=BLUE):
    def f(d, c):
        cross_with_gap(d, c, 240, 70, 40, color)
        d.polygon([(c, c - 70), (c + 70, c), (c, c + 70), (c - 70, c)], fill=color)
    return f


def x_marker(color=GREEN):
    def f(d, c):
        L, w = 210, 44
        d.line([c - L, c - L, c + L, c + L], fill=color, width=w)
        d.line([c - L, c + L, c + L, c - L], fill=color, width=w)
    return f


def ring_dot(color=WHITE, accent=RED):
    def f(d, c):
        d.ellipse([c - 90, c - 90, c + 90, c + 90], outline=accent, width=24)
        d.ellipse([c - 40, c - 40, c + 40, c + 40], fill=color)
    return f


DESIGNS = [
    ("dot-white", "Dot — Minimal", dot(WHITE)),
    ("dot-red", "Team Red — Dot", dot(RED)),
    ("dot-blue", "Team Blue — Dot", dot(BLUE)),
    ("classic-cross", "Classic Cross", classic(WHITE)),
    ("sniper-reticle", "Sniper Reticle", sniper(GREEN)),
    ("circle-dot", "Circle + Dot", circle_dot(WHITE)),
    ("diamond-center", "Diamond Center", diamond_center(BLUE)),
    ("x-marker", "Hit-marker X", x_marker(GREEN)),
    ("ring-dot", "Ring + Dot (two-tone)", ring_dot(WHITE, RED)),
]

# individual files
for name, label, fn in DESIGNS:
    render(fn).save(os.path.join(OUT, f"{name}.png"))

# composed sheet (3 cols)
CW, CH = 320, 320  # cell: 256 img + label band
cols = 3
rows = (len(DESIGNS) + cols - 1) // cols
sheet = Image.new("RGBA", (cols * CW, rows * CH), (14, 14, 20, 255))
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 26)
except Exception:
    font = ImageFont.load_default()

for i, (name, label, fn) in enumerate(DESIGNS):
    r, cidx = divmod(i, cols)
    x, y = cidx * CW, r * CH
    sheet.paste(render(fn), (x + (CW - 256) // 2, y + 12))
    tw = d.textlength(label, font=font)
    d.text((x + (CW - tw) // 2, y + 276), label, font=font, fill=(205, 205, 215, 255))

sheet.convert("RGB").save(os.path.join(OUT, "portfolio-sheet.jpg"), quality=92)
print(f"generated {len(DESIGNS)} crosshairs + sheet in {OUT}")
for n, _, _ in DESIGNS:
    print("  ", n + ".png")
print("   portfolio-sheet.jpg")
