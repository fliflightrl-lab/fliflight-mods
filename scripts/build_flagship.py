#!/usr/bin/env python3
"""
Build the flagship "PvP Essentials" resource pack.

Consolidates the three PROVEN winners into one all-in-one pack:
  1. Dot crosshair   (24,415 dl  - #1 pack)
  2. Visible ores    (13,045 dl  - hidden gem)
  3. Short sword     (5,698 dl)
Plus two high-demand PvP QoL additions:
  4. Low fire overlay
  5. Transparent pumpkin overlay

Output: a publishable .zip (resource pack layout) + pipeline manifest.json.

Run:  python3 scripts/build_flagship.py
"""
import os, io, json, zipfile, shutil
from PIL import Image, ImageDraw, ImageFont

BASE      = r"C:\Users\user\fliflight-mods"
PACKS     = os.path.join(BASE, "packs")
SLUG      = "pvp-essentials"
VERSION   = "1.0.5"
PACK_NAME = "PvP Essentials"
STAGE     = os.path.join(BASE, "build", SLUG)
DIST      = os.path.join(BASE, "dist")

# Proven source zips (assets already validated in the market)
SOURCES = {
    "dot":   r"dot-crosshair-cossx-better-crosshair/files/best_crosshair-1.0.0-resourcepack-1.21.4.zip",
    "ores":  r"visible-ores-all-versions-and-netherite/files/visible_ores-1.0.0-resourcepack-.zip",
    "sword": r"pvp-sword-little-sword-all-versions/files/better_little_sword-1.0.0-resourcepack-1.21.4.zip",
}

# ---------------------------------------------------------------- helpers
def extract_source(name, members, out_root):
    """Extract a curated set of members from a source zip into the staging tree."""
    src = os.path.join(PACKS, SOURCES[name])
    with zipfile.ZipFile(src) as z:
        for m in members:
            data = z.read(m)
            dest = os.path.join(out_root, m)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(data)
            print(f"  + {m}")

def png_bytes(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()

# ---------------------------------------------------------------- stage tree
if os.path.isdir(STAGE):
    shutil.rmtree(STAGE)
os.makedirs(STAGE, exist_ok=True)
os.makedirs(DIST, exist_ok=True)

print("[1/6] Crosshair — the 1px dot (new + legacy path fallback)")
extract_source("dot", ["assets/minecraft/textures/gui/sprites/hud/crosshair.png"], STAGE)
# also write to the legacy path (pre-1.20.5) as a harmless fallback
legacy = os.path.join(STAGE, "assets", "minecraft", "textures", "gui", "crosshair.png")
os.makedirs(os.path.dirname(legacy), exist_ok=True)
shutil.copy2(os.path.join(STAGE, "assets", "minecraft", "textures", "gui", "sprites", "hud", "crosshair.png"), legacy)
print("  + gui/crosshair.png (legacy fallback)")

print("[2/6] Visible ores (proven)")
with zipfile.ZipFile(os.path.join(PACKS, SOURCES["ores"])) as z:
    ore_members = [i.filename for i in z.infolist()
                   if not i.filename.endswith("/")
                   and (i.filename.startswith("assets/minecraft/textures/block/")
                        or i.filename.startswith("assets/minecraft/models/block/ancient_debris")
                        or i.filename.startswith("assets/minecraft/blockstates/"))]
extract_source("ores", ore_members, STAGE)

print("[3/6] Short swords (proven)")
extract_source("sword", [
    "assets/minecraft/textures/item/diamond_sword.png",
    "assets/minecraft/textures/item/golden_sword.png",
    "assets/minecraft/textures/item/iron_sword.png",
    "assets/minecraft/textures/item/netherite_sword.png",
    "assets/minecraft/textures/item/stone_sword.png",
    "assets/minecraft/textures/item/wooden_sword.png",
    "assets/minecraft/models/item/stone_sword.json",
], STAGE)

# ---------------------------------------------------------------- QoL: low fire
print("[4/6] Low fire overlay (QoL) — compress BOTH layers (full flame, shorter)")
# The user rejected TRUNCATION ("coupé" = the flame tip was cut off and it just
# stopped). Instead we VERTICALLY COMPRESS each frame: the WHOLE flame (tip AND
# base) is resized shorter, then bottom-aligned. Result: a complete, animating
# flame that sits LOWER instead of a chopped one.
# Both fire_0 (back flame) and fire_1 (front flame) are compressed so the whole
# flame is genuinely lower. The HUD "on fire" overlay reads these same block
# textures (block atlas), so the GUI is lowered automatically ("gui inclus").
VANILLA = os.path.join(BASE, "packs", "pvp-essentials", "vanilla_src")
COMPRESS_FRACTION = 0.6  # target flame height as a fraction of the 16px frame

for fn in ["fire_0.png", "fire_1.png"]:
    src = os.path.join(VANILLA, fn)
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    n = h // w                      # number of 16x16 frames in the strip
    new_h = max(1, round(w * COMPRESS_FRACTION))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for i in range(n):
        frame = img.crop((0, i * w, w, (i + 1) * w))        # full 16x16 frame
        compressed = frame.resize((w, new_h), Image.LANCZOS) # whole flame, shorter
        out.paste(compressed, (0, i * w + (w - new_h)))      # bottom-aligned
    img = out
    p = os.path.join(STAGE, "assets", "minecraft", "textures", "block", fn)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(png_bytes(img))
    print(f"  + assets/minecraft/textures/block/{fn} (compressed {w}px->{new_h}px, full shape)")

# CRITICAL: include the animation .mcmeta — without it the fire renders as a static,
# non-animating PNG (the user's "no animation" bug). Block fire and overlay share these.
for fn in ["fire_0.png", "fire_1.png"]:
    mc = os.path.join(VANILLA, fn + ".mcmeta")
    if os.path.exists(mc):
        shutil.copy2(mc, os.path.join(STAGE, "assets", "minecraft", "textures", "block", fn + ".mcmeta"))
        print(f"  + assets/minecraft/textures/block/{fn}.mcmeta (animation)")

# ---------------------------------------------------------------- QoL: no pumpkin
print("[5/6] Transparent pumpkin overlay (QoL)")
p = os.path.join(STAGE, "assets", "minecraft", "textures", "misc", "pumpkinblur.png")
os.makedirs(os.path.dirname(p), exist_ok=True)
with open(p, "wb") as f:
    f.write(png_bytes(Image.new("RGBA", (16, 16), (0, 0, 0, 0))))
print("  + assets/minecraft/textures/misc/pumpkinblur.png")

# ---------------------------------------------------------------- pack.mcmeta
print("[6/6] pack.mcmeta + pack.png")
pack_mcmeta = {
    "pack": {
        "pack_format": 46,
        "description": "PvP Essentials - better crosshair, visible ores, short sword, low fire",
    }
}
with open(os.path.join(STAGE, "pack.mcmeta"), "w", encoding="utf-8") as f:
    json.dump(pack_mcmeta, f, indent=2)

# ---- pack icon (128x128) : crosshair on a PvP gradient ----
icon = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
d = ImageDraw.Draw(icon)
# dark gradient bg
for y in range(128):
    t = y / 127.0
    r = int(16 + t * 8); g = int(18 + t * 10); b = int(30 + t * 20)
    d.line([(0, y), (128, y)], fill=(r, g, b, 255))
# rounded-ish square border
d.rounded_rectangle([14, 14, 114, 114], radius=16, outline=(0, 220, 180, 255), width=5)
# crosshair: circle + cross
d.ellipse([46, 46, 82, 82], outline=(0, 220, 180, 255), width=4)
d.line([(64, 28), (64, 44)], fill=(0, 220, 180, 255), width=4)
d.line([(64, 84), (64, 100)], fill=(0, 220, 180, 255), width=4)
d.line([(28, 64), (44, 64)], fill=(0, 220, 180, 255), width=4)
d.line([(84, 64), (100, 64)], fill=(0, 220, 180, 255), width=4)
d.ellipse([61, 61, 67, 67], fill=(255, 255, 255, 255))
with open(os.path.join(STAGE, "pack.png"), "wb") as f:
    f.write(png_bytes(icon))
print("  + pack.png (crosshair icon)")

# ---------------------------------------------------------------- zip it
zip_path = os.path.join(DIST, f"{SLUG}-{VERSION}-resourcepack-1.21.4.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(STAGE):
        for fn in files:
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, STAGE).replace("\\", "/")
            z.write(full, rel)

print(f"\nDONE -> {zip_path}  ({os.path.getsize(zip_path)} bytes)")
