"""Generate technical gallery renders for the two Fabric mods (no generative AI — programmatic drawings)."""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"C:\Users\user\fliflight-mods\dist\mod_gallery"
os.makedirs(OUT, exist_ok=True)
W, H = 1280, 720
BG = (16, 18, 26)

def font(sz):
    for name in ["arial.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(name, sz)
        except Exception:
            continue
    return ImageFont.load_default()

# ---------- 1. Custom Crosshair: 5 shapes ----------
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.text((W//2, 40), "Custom Crosshair - 5 shapes, one mod", font=font(34), fill=(255, 255, 255), anchor="mm")

shapes = [
    ("Cross", "cross"), ("Dot", "dot"), ("X", "x"),
    ("Circle", "circle"), ("T", "t"),
]
cy = H // 2
cx_pos = [W * i // 6 + W // 12 for i in range(5)]
white = (255, 255, 255)
for (label, shape), cx in zip(shapes, cx_pos):
    # draw vanilla-ish crosshair backdrop (faint)
    for dx in range(-30, 31, 10):
        d.line([(cx+dx, cy-34), (cx+dx, cy+34)], fill=(30, 34, 48), width=2)
    for dy in range(-30, 31, 10):
        d.line([(cx-34, cy+dy), (cx+34, cy+dy)], fill=(30, 34, 48), width=2)
    t = 5
    if shape == "cross":
        d.line([(cx, cy-22), (cx, cy-6)], fill=white, width=t)
        d.line([(cx, cy+6), (cx, cy+22)], fill=white, width=t)
        d.line([(cx-22, cy), (cx-6, cy)], fill=white, width=t)
        d.line([(cx+6, cy), (cx+22, cy)], fill=white, width=t)
    elif shape == "dot":
        d.ellipse([cx-4, cy-4, cx+4, cy+4], fill=white)
    elif shape == "x":
        d.line([(cx-18, cy-18), (cx-5, cy-5)], fill=white, width=t)
        d.line([(cx+5, cy+5), (cx+18, cy+18)], fill=white, width=t)
        d.line([(cx+18, cy-18), (cx+5, cy-5)], fill=white, width=t)
        d.line([(cx-5, cy+5), (cx-18, cy+18)], fill=white, width=t)
    elif shape == "circle":
        d.ellipse([cx-16, cy-16, cx+16, cy+16], outline=white, width=t)
    elif shape == "t":
        d.line([(cx-18, cy-18), (cx+18, cy-18)], fill=white, width=t)
        d.line([(cx, cy-18), (cx, cy+16)], fill=white, width=t)
    d.text((cx, cy + 60), label, font=font(26), fill=(200, 200, 210), anchor="mm")

d.text((W//2, H-40), "Change it in-game with the C key - color, size, thickness, presets",
       font=font(22), fill=(140, 145, 160), anchor="mm")
img.save(os.path.join(OUT, "custom-crosshair-shapes.png"))
print("saved custom-crosshair-shapes.png")

# ---------- 2. Custom Crosshair: settings GUI ----------
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.text((W//2, 36), "In-game settings screen (press C)", font=font(32), fill=(255, 255, 255), anchor="mm")

# panel
px, py, pw, ph = 340, 90, 600, 540
d.rounded_rectangle([px, py, px+pw, py+ph], radius=12, fill=(26, 30, 42), outline=(60, 66, 88), width=2)
d.text((px+24, py+18), "Crosshair Settings", font=font(28), fill=(255, 255, 255))
rows = ["Shape:  Cross", "Color:  #FF5555", "Size:  12", "Thickness:  5", "Gap:  4", "Center dot:  ON", "Preset:  Valorant"]
yy = py + 90
for i, r_ in enumerate(rows):
    d.text((px+24, yy), r_, font=font(24), fill=(190, 195, 210))
    d.line([(px+24, yy+40), (px+pw-24, yy+40)], fill=(44, 50, 68), width=2)
    yy += 64

# preview area (right of panel)
prx = px + pw + 60
d.rounded_rectangle([prx-60, py, prx+200, py+300], radius=12, fill=(26, 30, 42), outline=(60, 66, 88), width=2)
d.text((prx+40, py+16), "Live preview", font=font(22), fill=(200, 200, 210))
vx, vy = prx + 70, py + 170
d.line([(vx, vy-20), (vx, vy-5)], fill=(255, 85, 85), width=5)
d.line([(vx, vy+5), (vx, vy+20)], fill=(255, 85, 85), width=5)
d.line([(vx-20, vy), (vx-5, vy)], fill=(255, 85, 85), width=5)
d.line([(vx+5, vy), (vx+20, vy)], fill=(255, 85, 85), width=5)

img.save(os.path.join(OUT, "custom-crosshair-gui.png"))
print("saved custom-crosshair-gui.png")

# ---------- 3. PvP HUD ----------
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.text((W//2, 36), "PvP HUD - everything you need, top-left", font=font(32), fill=(255, 255, 255), anchor="mm")

# fake game backdrop (subtle gradient bars)
for i in range(0, H, 8):
    shade = 20 + (i % 40)
    d.rectangle([0, i, W, i+8], fill=(shade, shade+2, shade+6))
# horizon line mock
d.line([(0, H//2), (W, H//2)], fill=(45, 50, 66), width=3)

# HUD panel top-left
hx, hy = 40, 90
d.rounded_rectangle([hx, hy, hx+300, hy+190], radius=10, fill=(0, 0, 0, 0), outline=None)
# semi-transparent look via solid dark
d.rounded_rectangle([hx, hy, hx+300, hy+190], radius=10, fill=(10, 12, 18), outline=(70, 76, 96), width=2)
lines = [
    ("FPS", "144", (140, 255, 140)),
    ("Ping", "23 ms", (255, 220, 120)),
    ("XYZ", "124 64 -318", (130, 190, 255)),
    ("CPS", "12 L / 9 R", (255, 130, 130)),
]
yy = hy + 18
for name, val, col in lines:
    d.text((hx+16, yy), name, font=font(22), fill=(170, 175, 190))
    d.text((hx+150, yy), val, font=font(24), fill=col)
    yy += 42

d.text((W//2, H-40), "All lines are toggleable in config/pvphud.json",
       font=font(22), fill=(140, 145, 160), anchor="mm")
img.save(os.path.join(OUT, "pvphud-hud.png"))
print("saved pvphud-hud.png")
