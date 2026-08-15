#!/usr/bin/env python3
"""Build the two standalone QoL packs:
  1. fliflight-low-fire      -> compressed fire_0/fire_1 (+ .mcmeta), full flame, lowered
  2. fliflight-clear-pumpkin -> transparent pumpkinblur overlay

Each gets: resource-pack zip, pack.png icon (from the REAL textures), 1 gallery
image (real textures, before/after), and a manifest.json pointing to PvP Essentials
as the all-in-one (funnel strategy).

Run:  python3 scripts/build_standalone_qol.py
"""
import os, io, json, zipfile, shutil
from PIL import Image

BASE  = r"C:\Users\user\fliflight-mods"
PACKS = os.path.join(BASE, "packs")
DIST  = os.path.join(BASE, "dist")
VANILLA = os.path.join(PACKS, "pvp-essentials", "vanilla_src")
COMPRESS_FRACTION = 0.6
PACK_FORMAT = 46
GAME_VERSIONS = ["1.19","1.19.2","1.19.4","1.20","1.20.1","1.20.2","1.20.4","1.20.5",
                 "1.20.6","1.21","1.21.1","1.21.3","1.21.4","1.21.5","1.21.6",
                 "1.21.7","1.21.8"]

def png_bytes(img):
    buf = io.BytesIO(); img.save(buf, "PNG"); return buf.getvalue()

def zip_dir(stage, zip_path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(stage):
            for fn in files:
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, stage).replace("\\", "/")
                z.write(full, rel)
    print(f"  -> {zip_path} ({os.path.getsize(zip_path)} bytes)")

def write_pack_mcmeta(stage, desc):
    os.makedirs(stage, exist_ok=True)
    with open(os.path.join(stage, "pack.mcmeta"), "w", encoding="utf-8") as f:
        json.dump({"pack": {"pack_format": PACK_FORMAT, "description": desc}}, f, indent=2)

def compress_fire(src, dst, fraction):
    """Vertical-compress every frame of a 16x512 fire strip, keep full shape, bottom-align."""
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    n = h // w
    new_h = max(1, round(w * fraction))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for i in range(n):
        frame = img.crop((0, i * w, w, (i + 1) * w))
        compressed = frame.resize((w, new_h), Image.LANCZOS)
        out.paste(compressed, (0, i * w + (w - new_h)))
    out.save(dst)
    return out

def fire_frame_png(fraction, index=0):
    """Return a PIL Image of one full flame frame (compressed) for icon/gallery use."""
    src = os.path.join(VANILLA, "fire_0.png")
    img = Image.open(src).convert("RGBA")
    w = img.size[0]
    frame = img.crop((0, index * w, w, (index + 1) * w))
    new_h = max(1, round(w * fraction))
    canvas = Image.new("RGBA", (w, w), (0, 0, 0, 0))
    canvas.paste(frame.resize((w, new_h), Image.LANCZOS), (0, w - new_h))
    return canvas

# ================================================================ 1. LOW FIRE
print("=" * 60)
print("[1] fliflight-low-fire")
SLUG = "fliflight-low-fire"
STAGE = os.path.join(BASE, "build", SLUG)
if os.path.isdir(STAGE): shutil.rmtree(STAGE)
os.makedirs(os.path.join(STAGE, "assets", "minecraft", "textures", "block"), exist_ok=True)

for fn in ["fire_0.png", "fire_1.png"]:
    compress_fire(os.path.join(VANILLA, fn),
                  os.path.join(STAGE, "assets", "minecraft", "textures", "block", fn),
                  COMPRESS_FRACTION)
    shutil.copy2(os.path.join(VANILLA, fn + ".mcmeta"),
                 os.path.join(STAGE, "assets", "minecraft", "textures", "block", fn + ".mcmeta"))
    print(f"  + {fn} (compressed) + .mcmeta")

write_pack_mcmeta(STAGE, "Low Fire - lowers the fire overlay (world + GUI), full flame animation")

# icon: the compressed flame on dark bg
icon = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
d = Image.new("RGBA", (128, 128), (14, 14, 18, 255))
flame = fire_frame_png(COMPRESS_FRACTION).resize((88, 88), Image.NEAREST)
d.paste(flame, ((128 - 88) // 2, 128 - 88 - 6), flame)  # bottom-aligned-ish
d.save(os.path.join(STAGE, "pack.png"))
print("  + pack.png")

# gallery: before (vanilla) vs after (compressed) with labels
def gallery_compare(out_path, label_left, img_left, label_right, img_right):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    S = 800
    g = Image.new("RGBA", (S, S), (10, 10, 12, 255))
    half = S // 2
    for img, cx, label in [(img_left, half // 2, label_left), (img_right, half + half // 2, label_right)]:
        px = int(S * 0.36)
        im = img.resize((px, px), Image.NEAREST)
        g.paste(im, (cx - px // 2, S // 2 - px // 2), im)
        # simple label bar
        from PIL import ImageDraw, ImageFont
        dr = ImageDraw.Draw(g)
        bar_w = int(px * 0.9)
        x0 = cx - bar_w // 2
        dr.rectangle([x0, S - 90, x0 + bar_w, S - 30], fill=(24, 24, 30, 255))
        try:
            font = ImageFont.truetype("arialbd.ttf", 34)
        except Exception:
            font = ImageFont.load_default()
        tb = dr.textbbox((0, 0), label, font=font)
        dr.text((cx - (tb[2] - tb[0]) // 2, S - 82 + (58 - (tb[3] - tb[1])) // 2), label,
                fill=(255, 255, 255, 255), font=font)
        dr.line([(half, S // 4), (half, S * 3 // 4)], fill=(60, 60, 70, 255), width=3)
    g.convert("RGB").save(out_path)
    print(f"  + gallery {os.path.basename(out_path)}")

gallery_compare(os.path.join(PACKS, SLUG, "gallery", "01_lowfire.png"),
                "Vanilla", Image.open(os.path.join(VANILLA, "fire_0.png")).convert("RGBA").crop((0, 0, 16, 16)),
                "Low Fire", fire_frame_png(COMPRESS_FRACTION))

VERSION = "1.0.0"
zip_path = os.path.join(DIST, f"{SLUG}-{VERSION}-resourcepack-1.21.4.zip")
zip_dir(STAGE, zip_path)
os.makedirs(os.path.join(PACKS, SLUG, "files"), exist_ok=True)
shutil.copy2(zip_path, os.path.join(PACKS, SLUG, "files", os.path.basename(zip_path)))
shutil.copy2(os.path.join(STAGE, "pack.png"), os.path.join(PACKS, SLUG, "icon.png"))

manifest = {
    "slug": SLUG,
    "name": "Low Fire — Lowered Flame Overlay (Full Animation)",
    "project_type": "resourcepack",
    "summary": "Lowers the fire overlay (in-world and GUI) so it never blocks your view — full flame, full animation, just shorter.",
    "body": "Tired of the vanilla fire taking over your whole screen? This pack **lowers the flame** while keeping the complete fire animation.\\n\\n- 🔥 **Lowered flame** — the whole fire sits lower, tip and animation intact (no cut-off flame)\\n- 🖥️ **GUI included** — the on-screen fire overlay is lowered too\\n- ✅ **Works on every launcher** — just drop in `resourcepacks` and enable\\n\\n---\\n\\n### 🚀 Want everything in one pack?\\nThis feature is part of **[PvP Essentials](https://www.curseforge.com/minecraft/texture-packs/fliflight-pvp-essentials)** — the all-in-one pack with crosshair, visible ores, short sword, low fire and clear pumpkin.\\n> 💡 **CurseForge is the source of truth** for this pack — the most up-to-date, bug-free versions are always there first: [CurseForge page](https://www.curseforge.com/minecraft/texture-packs/fliflight-low-fire)",
    "license": "All Rights Reserved",
    "categories": ["utility", "16x"],
    "curseforge_id": None,
    "modrinth_id": None,
    "links": {
        "website_url": "https://www.curseforge.com/members/fliflightmc/projects",
        "source_url": None, "issues_url": None, "wiki_url": "",
    },
    "version": {
        "number": VERSION, "type": "release",
        "changelog": "Initial release: lowered fire overlay with full animation (world + GUI).",
        "loaders": ["minecraft"], "game_versions": GAME_VERSIONS,
    },
    "file": os.path.basename(zip_path),
    "icon": "icon.png",
    "gallery": ["01_lowfire.png"],
}
with open(os.path.join(PACKS, SLUG, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)
print("  + manifest.json")

# ================================================================ 2. CLEAR PUMPKIN
print("=" * 60)
print("[2] fliflight-clear-pumpkin")
SLUG = "fliflight-clear-pumpkin"
STAGE = os.path.join(BASE, "build", SLUG)
if os.path.isdir(STAGE): shutil.rmtree(STAGE)
misc = os.path.join(STAGE, "assets", "minecraft", "textures", "misc")
os.makedirs(misc, exist_ok=True)
Image.new("RGBA", (16, 16), (0, 0, 0, 0)).save(os.path.join(misc, "pumpkinblur.png"))
print("  + pumpkinblur.png (fully transparent)")
write_pack_mcmeta(STAGE, "Clear Pumpkin - no more pumpkin blur when you wear one")

# icon: real carved pumpkin texture, no blur
pumpkin = Image.open(os.path.join(PACKS, "pvp-essentials", "gallery_src", "vanilla", "carved_pumpkin.png")).convert("RGBA")
d = Image.new("RGBA", (128, 128), (14, 14, 18, 255))
pm = pumpkin.resize((100, 100), Image.NEAREST)
d.paste(pm, ((128 - 100) // 2, (128 - 100) // 2), pm)
d.save(os.path.join(STAGE, "pack.png"))
print("  + pack.png")

# gallery: pumpkin WITH blur (vanilla overlay) vs WITHOUT (this pack)
def with_blur():
    """carved pumpkin + semi-transparent orange blur overlay (vanilla effect)."""
    src = os.path.join(PACKS, "pvp-essentials", "gallery_src", "vanilla", "carved_pumpkin.png")
    base = Image.open(src).convert("RGBA").resize((16, 16), Image.NEAREST)
    blur = Image.new("RGBA", (16, 16), (255, 120, 20, 110))
    base.alpha_composite(blur)
    return base

gallery_compare(os.path.join(PACKS, SLUG, "gallery", "01_pumpkin.png"),
                "Vanilla", with_blur(),
                "Clear Pumpkin", Image.open(os.path.join(PACKS, "pvp-essentials", "gallery_src", "vanilla", "carved_pumpkin.png")).convert("RGBA"))

VERSION = "1.0.0"
zip_path = os.path.join(DIST, f"{SLUG}-{VERSION}-resourcepack-1.21.4.zip")
zip_dir(STAGE, zip_path)
os.makedirs(os.path.join(PACKS, SLUG, "files"), exist_ok=True)
shutil.copy2(zip_path, os.path.join(PACKS, SLUG, "files", os.path.basename(zip_path)))
shutil.copy2(os.path.join(STAGE, "pack.png"), os.path.join(PACKS, SLUG, "icon.png"))

manifest = {
    "slug": SLUG,
    "name": "Clear Pumpkin — No Pumpkin Blur",
    "project_type": "resourcepack",
    "summary": "Removes the orange pumpkin blur overlay so you can see clearly while wearing a pumpkin.",
    "body": "Wearing a pumpkin for the Enderman trick? The vanilla orange blur makes it hard to see. This pack **removes the blur entirely**.\\n\\n- 🎃 **No more orange overlay** — full clear vision\\n- ✅ **Works on every launcher** — just drop in `resourcepacks` and enable\\n\\n---\\n\\n### 🚀 Want everything in one pack?\\nThis feature is part of **[PvP Essentials](https://www.curseforge.com/minecraft/texture-packs/fliflight-pvp-essentials)** — the all-in-one pack with crosshair, visible ores, short sword, low fire and clear pumpkin.\\n> 💡 **CurseForge is the source of truth** for this pack — the most up-to-date, bug-free versions are always there first: [CurseForge page](https://www.curseforge.com/minecraft/texture-packs/fliflight-clear-pumpkin)",
    "license": "All Rights Reserved",
    "categories": ["utility", "16x"],
    "curseforge_id": None,
    "modrinth_id": None,
    "links": {
        "website_url": "https://www.curseforge.com/members/fliflightmc/projects",
        "source_url": None, "issues_url": None, "wiki_url": "",
    },
    "version": {
        "number": VERSION, "type": "release",
        "changelog": "Initial release: removes the pumpkin blur overlay entirely.",
        "loaders": ["minecraft"], "game_versions": GAME_VERSIONS,
    },
    "file": os.path.basename(zip_path),
    "icon": "icon.png",
    "gallery": ["01_pumpkin.png"],
}
with open(os.path.join(PACKS, SLUG, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)
print("  + manifest.json")

print("\nALL DONE")
