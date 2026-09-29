#!/usr/bin/env python3
"""Redesign the pack icons: black background + the item in the foreground,
with a red strike-through bar for the packs that REMOVE something.

Outputs per pack:
  - pack.png  128x128  (goes inside the zip / in-game list)
  - dist/cf_logos/<slug>-512.png  512x512  (CurseForge project avatar + name)
"""
import os, io, zipfile
from PIL import Image, ImageDraw, ImageFont

BASE = r"C:\Users\user\fliflight-mods"
PACKS = os.path.join(BASE, "packs")
JAR = os.path.join(BASE, "build", "client-1.21.4.jar")
S = "assets/minecraft/textures/"
BG = (13, 14, 18)
RED = (226, 62, 62)

def vimg(rel):
    with zipfile.ZipFile(JAR) as z:
        return Image.open(io.BytesIO(z.read(S + rel))).convert("RGBA")

def vframe(rel, frame=0, size=16):
    """first frame of an animated vanilla texture"""
    im = vimg(rel)
    return im.crop((0, frame * size, size, (frame + 1) * size))

def font(sz):
    for n in ["arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"]:
        try:
            return ImageFont.truetype(n, sz)
        except Exception:
            continue
    return ImageFont.load_default()

def barre(img, w=None):
    """draw a red strike-through with a dark outline"""
    W, H = img.size
    t = int(W * 0.115)          # bar thickness
    out = int(W * 0.022)        # outline
    d = ImageDraw.Draw(img)
    pad = int(W * 0.14)
    p1 = (pad, H - pad)
    p2 = (W - pad, pad)
    d.line([p1, p2], fill=(10, 10, 12, 255), width=t + out * 2)
    d.line([p1, p2], fill=RED + (255,), width=t)
    return img

def screen_with_dark_corners(size):
    """a mock screen whose corners are darkened (the vanilla vignette look)"""
    im = Image.new("RGBA", (size, size), (78, 82, 96, 255))
    d = ImageDraw.Draw(im)
    c = size / 2
    maxr = size * 0.72
    r = maxr
    while r > 0:
        a = int(215 * (1 - r / maxr) ** 1.7)
        d.ellipse([c - r, c - r, c + r, c + r], outline=(0, 0, 0, a), width=max(2, size // 90))
        r -= max(2, size // 90)
    return im

def frost_overlay(size):
    """the vanilla frost/powder-snow overlay look"""
    im = Image.new("RGBA", (size, size), (60, 66, 82, 255))
    d = ImageDraw.Draw(im)
    c = size / 2
    maxr = size * 0.72
    r = maxr
    while r > 0:
        a = int(200 * (1 - r / maxr) ** 1.7)
        d.ellipse([c - r, c - r, c + r, c + r], outline=(228, 240, 255, a), width=max(2, size // 90))
        r -= max(2, size // 90)
    return im

def hotbar_art(size):
    """the clean flat hotbar as an icon (lightened so it reads on the dark icon bg)"""
    W = size
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bar_w = int(W * 0.88)
    bar_h = int(bar_w * 22 / 182)
    x0 = (W - bar_w) // 2
    y0 = (W - bar_h) // 2
    slot = bar_w / 9
    for i in range(9):
        sx = x0 + i * slot
        d.rectangle([sx + 1, y0 + 1, sx + slot - 3, y0 + bar_h - 2],
                    fill=(52, 57, 71, 255), outline=(196, 203, 222, 255), width=max(2, W // 120))
    # xp bar under it
    xh = max(3, W // 60)
    d.rectangle([x0, y0 + bar_h + xh * 2, x0 + bar_w, y0 + bar_h + xh * 3], fill=(38, 42, 53, 255))
    d.rectangle([x0, y0 + bar_h + xh * 2, x0 + int(bar_w * 0.45), y0 + bar_h + xh * 3], fill=(122, 236, 106, 255))
    return im

def shield_art(size):
    return vimg("entity/shield_base.png").resize((size, size), Image.NEAREST)

def water_art(size):
    return vframe("block/water_still.png").resize((size, size), Image.NEAREST)

def lava_art(size):
    return vframe("block/lava_still.png").resize((size, size), Image.NEAREST)

def scope_art(size):
    """the black spyglass scope over a light 'view' so it reads at icon size"""
    view = Image.new("RGBA", (size, size), (92, 138, 78, 255))
    dd = ImageDraw.Draw(view)
    for i in range(0, size, max(4, size // 12)):
        dd.line([(0, i), (size, i)], fill=(84, 128, 72, 255), width=2)
    sc = vimg("misc/spyglass_scope.png").resize((size, size), Image.NEAREST)
    view.alpha_composite(sc)
    return view

def totem_thin_art(size):
    tot = vimg("item/totem_of_undying.png")
    thin = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    sm = tot.resize((7, 16), Image.LANCZOS)
    thin.paste(sm, (4, 0), sm)
    return thin.resize((size, size), Image.NEAREST)

def pumpkin_art(size):
    p = os.path.join(PACKS, "pvp-essentials", "gallery_src", "vanilla", "carved_pumpkin.png")
    return Image.open(p).convert("RGBA").resize((size, size), Image.NEAREST)

# slug -> (art builder, strike-through?, label for the 512 CF logo)
PACKS_PLAN = {
    "fliflight-low-shield":        (shield_art,            True,  "LOW SHIELD"),
    "fliflight-clear-water":       (water_art,             True,  "CLEAR WATER"),
    "fliflight-clear-lava":        (lava_art,              True,  "CLEAR LAVA"),
    "fliflight-clear-spyglass":    (scope_art,             True,  "CLEAR SPYGLASS"),
    "fliflight-clear-powder-snow": (frost_overlay,         True,  "CLEAR POWDER SNOW"),
    "fliflight-thin-totem":        (totem_thin_art,        False, "THIN TOTEM"),
    "fliflight-clean-hotbar":      (hotbar_art,            False, "CLEAN HOTBAR"),
}

def make(slug, art_fn, strike, label, label_font_size=40):
    """128 pack.png + 512 CF logo"""
    # --- 128 in-game icon: bg + art centred, ~86% of the canvas
    icon = Image.new("RGBA", (128, 128), BG + (255,))
    art = art_fn(104)
    icon.paste(art, ((128 - art.size[0]) // 2, (128 - art.size[1]) // 2), art)
    if strike:
        barre(icon)
    icon.save(os.path.join(PACKS, slug, "pack.png"))
    print(f"  {slug}/pack.png (128) {'+ barre' if strike else ''}")

    # --- 512 CF logo: same look, roomier, + the pack name
    logo = Image.new("RGBA", (512, 512), BG + (255,))
    d = ImageDraw.Draw(logo)
    # subtle glow so it is not a flat square (CF refuses solid-colour avatars)
    for r in range(250, 60, -10):
        a = 10 + int((250 - r) / 6)
        d.ellipse([256 - r, 226 - r, 256 + r, 226 + r], fill=(18 + a, 21 + a, 30 + a, 255))
    art = art_fn(300)
    logo.paste(art, ((512 - art.size[0]) // 2, 226 - art.size[1] // 2), art)
    if strike:
        barre(logo)
    f = font(label_font_size)
    tb = d.textbbox((0, 0), label, font=f)
    d.text(((512 - (tb[2] - tb[0])) // 2, 512 - 92), label, fill=(238, 240, 246, 255), font=f)
    out = os.path.join(BASE, "dist", "cf_logos", slug + "-512.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    logo.convert("RGB").save(out)
    print(f"  {slug}-512.png (CF)")

for slug, (art_fn, strike, label) in PACKS_PLAN.items():
    make(slug, art_fn, strike, label)

# no-vignette needs its own art (a screen with dark corners)
make("fliflight-no-vignette", screen_with_dark_corners, True, "NO DARK CORNERS")

# also refresh Clear Pumpkin in the same language
make("fliflight-clear-pumpkin", pumpkin_art, True, "CLEAR PUMPKIN", 38)

print("DONE — icons regenerated")
