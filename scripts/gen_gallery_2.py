#!/usr/bin/env python3
"""Generate a SECOND gallery image per pack (different scene) to satisfy
CurseForge/Modrinth 'insufficient gallery images' + give every image a label.

Reuses the real vanilla 1.21.4 textures so the render stays an accurate
representation of the pack's content.
"""
import os, io, zipfile
from PIL import Image, ImageDraw, ImageFont

BASE = r"C:\Users\user\fliflight-mods"
PACKS = os.path.join(BASE, "packs")
JAR = os.path.join(BASE, "build", "client-1.21.4.jar")
S = "assets/minecraft/textures/"

def vimg(rel):
    with zipfile.ZipFile(JAR) as z:
        return Image.open(io.BytesIO(z.read(S + rel))).convert("RGBA")

def font(sz):
    for n in ["arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(n, sz)
        except Exception:
            continue
    return ImageFont.load_default()

def tile(img, size):
    w, h = img.size
    out = Image.new("RGBA", size)
    for y in range(0, size[1], h):
        for x in range(0, size[0], w):
            out.paste(img, (x, y))
    return out

def panel(before, after, lb, rb, caption, out_path):
    """800x800 before/after panel."""
    W = 800
    g = Image.new("RGBA", (W, W), (10, 10, 12, 255))
    d = ImageDraw.Draw(g)
    half = W // 2
    size = 300
    for img, cx, label in [(before, half // 2, lb), (after, half + half // 2, rb)]:
        im = img.convert("RGBA").resize((size, size), Image.NEAREST)
        g.paste(im, (cx - size // 2, 150), im)
        d.rectangle([cx - size // 2 - 2, 148, cx + size // 2 + 1, 150 + size], outline=(70, 74, 92), width=2)
        d.rectangle([cx - size // 2, 500, cx + size // 2, 556], fill=(24, 24, 30, 255))
        f = font(30)
        tb = d.textbbox((0, 0), label, font=f)
        d.text((cx - (tb[2] - tb[0]) // 2, 528 - (tb[3] - tb[1]) // 2 - 6), label, fill=(255, 255, 255, 255), font=f)
    d.line([(half, 140), (half, 570)], fill=(60, 60, 70, 255), width=3)
    f = font(26)
    tb = d.textbbox((0, 0), caption, font=f)
    d.text((W // 2 - (tb[2] - tb[0]) // 2, 640), caption, fill=(150, 155, 170, 255), font=f)
    g.convert("RGB").save(out_path)
    print("  +", os.path.basename(out_path))

# ---------------------------------------------------------------- scenes
def dusk(img):
    """darken a scene (night mood)"""
    ov = Image.new("RGBA", img.size, (6, 8, 22, 130))
    base = img.copy(); base.alpha_composite(ov); return base

def icy(img):
    ov = Image.new("RGBA", img.size, (210, 235, 255, 90))
    base = img.copy(); base.alpha_composite(ov); return base

# 1. LOW SHIELD — fight over grass
bg = tile(vimg("block/grass_block_side.png"), (300, 300))
sh = vimg("entity/shield_base.png")
def shield_scene(scale):
    b = bg.copy()
    im = sh.resize((int(150 * scale), int(150 * scale)), Image.NEAREST)
    b.alpha_composite(im, (150 - im.size[0] // 2, 300 - im.size[1] + int(40 * scale)))
    return b
panel(shield_scene(1.25), shield_scene(0.7), "Vanilla", "Low Shield",
      "In a fight: the shield stays small and low, your target stays visible",
      os.path.join(PACKS, "fliflight-low-shield", "gallery", "02_fight.png"))

# 2. NO VIGNETTE — night cave
cave = dusk(tile(vimg("block/deepslate.png"), (300, 300)))
def vign(alpha_mul=1.0):
    b = cave.copy()
    ov = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    for r in range(150, 0, -3):
        a = int(210 * alpha_mul * (1 - r / 150.0) ** 2)
        dd.ellipse([150 - r * 1.15, 150 - r * 1.15, 150 + r * 1.15, 150 + r * 1.15], outline=(0, 0, 0, a), width=4)
    b.alpha_composite(ov); return b
panel(vign(1.0), vign(0.0), "Vanilla", "No Vignette",
      "In a deep cave: no corner shading, everything stays readable",
      os.path.join(PACKS, "fliflight-no-vignette", "gallery", "02_night.png"))

# 3. CLEAR WATER — underwater over stone
seabed = tile(vimg("block/stone.png"), (300, 300))
def water(a):
    b = seabed.copy(); b.alpha_composite(Image.new("RGBA", (300, 300), (48, 92, 200, a))); return b
panel(water(190), water(38), "Vanilla", "Clear Water",
      "Underwater: see the terrain and mineshafts around you",
      os.path.join(PACKS, "fliflight-clear-water", "gallery", "02_underwater.png"))

# 4. CLEAR LAVA — nether
nether = tile(vimg("block/blackstone.png"), (300, 300))
def lava(a):
    b = nether.copy(); b.alpha_composite(Image.new("RGBA", (300, 300), (207, 92, 16, a))); return b
panel(lava(255), lava(110), "Vanilla", "Clear Lava",
      "In the Nether: spot the terrain before you cross",
      os.path.join(PACKS, "fliflight-clear-lava", "gallery", "02_nether.png"))

# 5. CLEAR SPYGLASS — distant forest view
forest = tile(vimg("block/oak_leaves.png"), (300, 300))
def scope(show):
    b = forest.copy()
    if show:
        mask = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
        mask.paste(Image.new("RGBA", (300, 300), (0, 0, 0, 215)), (0, 0))
        hole = Image.new("L", (300, 300), 255)
        ImageDraw.Draw(hole).ellipse([70, 70, 230, 230], fill=0)
        mask.putalpha(Image.composite(Image.new("L", (300, 300), 215), Image.new("L", (300, 300), 0), hole))
        b.alpha_composite(mask)
    return b
panel(scope(True), scope(False), "Vanilla", "Clear Spyglass",
      "Zoomed in: the full screen stays usable, spot players from far away",
      os.path.join(PACKS, "fliflight-clear-spyglass", "gallery", "02_zoom.png"))

# 6. CLEAN HOTBAR — with items in it
def hotbar_with_items(clean):
    c = Image.new("RGBA", (300, 300), (12, 12, 16, 255))
    if clean:
        bar = Image.new("RGBA", (182, 22), (0, 0, 0, 0))
        dr = ImageDraw.Draw(bar)
        for i in range(9):
            x0 = 1 + i * 20
            dr.rectangle([x0, 1, x0 + 18, 20], fill=(12, 12, 16, 170), outline=(90, 94, 110, 210))
    else:
        bar = vimg("gui/sprites/hud/hotbar.png").convert("RGBA")
    bar = bar.resize((270, 33), Image.NEAREST)
    c.paste(bar, (15, 210), bar)
    # a few item icons sitting in the slots
    items = [("item/diamond_sword.png", 0), ("item/golden_apple.png", 1), ("item/ender_pearl.png", 2),
             ("item/cooked_beef.png", 3), ("block/cobblestone.png", 4)]
    for rel, slot in items:
        try:
            it = vimg(rel).resize((28, 28), Image.NEAREST)
            c.paste(it, (17 + slot * 30, 213), it)
        except Exception:
            pass
    return c
panel(hotbar_with_items(False), hotbar_with_items(True), "Vanilla", "Clean Hotbar",
      "In game with items: same 9 slots, far less visual noise",
      os.path.join(PACKS, "fliflight-clean-hotbar", "gallery", "02_items.png"))

# 7. THIN TOTEM — in a fight at night
fight = dusk(tile(vimg("block/grass_block_side.png"), (300, 300)))
tot = vimg("item/totem_of_undying.png")
def totem_scene(thin):
    b = fight.copy()
    im = (Image.new("RGBA", (16, 16), (0, 0, 0, 0)) if thin else tot.copy())
    if thin:
        sm = tot.resize((7, 16), Image.LANCZOS); im.paste(sm, (4, 0), sm)
    for (x, y, s) in [(150, 150, 110), (210, 110, 60)]:
        z = im.resize((s, s), Image.NEAREST)
        b.alpha_composite(z, (x - s // 2, y - s // 2))
    return b
panel(totem_scene(False), totem_scene(True), "Vanilla", "Thin Totem",
      "Popping a totem mid-fight: the slimmer one leaves your view clear",
      os.path.join(PACKS, "fliflight-thin-totem", "gallery", "02_fight.png"))

# 8. CLEAR POWDER SNOW — snowy mountain at night
snowm = dusk(tile(vimg("block/snow.png"), (300, 300)))
def frost(show):
    b = snowm.copy()
    if show:
        ov = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
        dd = ImageDraw.Draw(ov)
        for r in range(150, 0, -3):
            a = int(180 * (1 - r / 150.0) ** 2)
            dd.ellipse([150 - r * 1.15, 150 - r * 1.15, 150 + r * 1.15, 150 + r * 1.15], outline=(225, 240, 255, a), width=4)
        b.alpha_composite(ov)
    return b
panel(frost(True), frost(False), "Vanilla", "Clear Powder Snow",
      "Freezing at night: no frost veil, you can still see the way out",
      os.path.join(PACKS, "fliflight-clear-powder-snow", "gallery", "02_night.png"))

# 9. CLEAR PUMPKIN (the one that got rejected) — pumpkin view at night
night_grass = dusk(tile(vimg("block/grass_block_side.png"), (300, 300)))
pump = vimg("gallery_src/vanilla/carved_pumpkin.png") if False else None
def pumpkin_scene(blur):
    b = night_grass.copy()
    if blur:
        b.alpha_composite(Image.new("RGBA", (300, 300), (255, 120, 20, 110)))
    # pumpkin frame around the view
    ov = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    dd.rectangle([0, 0, 300, 26], fill=(196, 120, 40, 235))
    dd.rectangle([0, 274, 300, 300], fill=(196, 120, 40, 235))
    dd.rectangle([0, 0, 26, 300], fill=(196, 120, 40, 235))
    dd.rectangle([274, 0, 300, 300], fill=(196, 120, 40, 235))
    b.alpha_composite(ov)
    return b
panel(pumpkin_scene(True), pumpkin_scene(False), "Vanilla", "Clear Pumpkin",
      "Wearing a pumpkin at night: the orange blur is gone, mobs stay visible",
      os.path.join(PACKS, "fliflight-clear-pumpkin", "gallery", "02_night.png"))

print("DONE — second gallery image per pack")
