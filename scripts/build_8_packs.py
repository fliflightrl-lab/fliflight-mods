#!/usr/bin/env python3
"""Build 8 new Fliflight resource packs from REAL vanilla 1.21.4 textures.

  1. fliflight-low-shield       - smaller first-person shield (model display transform)
  2. fliflight-no-vignette      - removes the corner darkening
  3. fliflight-clear-water      - see-through water + clear underwater overlay
  4. fliflight-clear-lava       - see-through lava
  5. fliflight-clear-spyglass   - no scope overlay when using a spyglass
  6. fliflight-clean-hotbar     - flat clean hotbar + XP bar
  7. fliflight-thin-totem       - thinner totem so the pop animation blocks less
  8. fliflight-clear-powder-snow- removes the frost overlay when freezing

Each: zip, pack.png icon, 800x800 before/after gallery (real textures), manifest.
Run:  python scripts/build_8_packs.py
"""
import os, io, json, zipfile, shutil
from PIL import Image, ImageDraw, ImageFont

BASE   = r"C:\Users\user\fliflight-mods"
PACKS  = os.path.join(BASE, "packs")
DIST   = os.path.join(BASE, "dist")
BUILD  = os.path.join(BASE, "build")
JAR    = os.path.join(BUILD, "client-1.21.4.jar")
S      = "assets/minecraft/textures/"
PACK_FORMAT = 46

V_WIDE = ["1.19","1.19.2","1.19.4","1.20","1.20.1","1.20.2","1.20.4","1.20.5","1.20.6",
          "1.21","1.21.1","1.21.3","1.21.4","1.21.5","1.21.6","1.21.7","1.21.8"]
V_MODERN = ["1.21.3","1.21.4","1.21.5","1.21.6","1.21.7","1.21.8"]

CF_FLAGSHIP = "https://www.curseforge.com/minecraft/texture-packs/pvp-essentials-crosshair-visible-ores-sword-low"
CF_MEMBER   = "https://www.curseforge.com/members/fliflightmc/projects"


# ---------------------------------------------------------------- helpers
def vanilla(path):
    """Raw bytes of a vanilla asset."""
    with zipfile.ZipFile(JAR) as z:
        return z.read(path)


def vimg(rel):
    """Vanilla texture as RGBA image."""
    return Image.open(io.BytesIO(vanilla(S + rel))).convert("RGBA")


def vmeta(rel):
    return vanilla(S + rel + ".mcmeta")


def save_meta(stage, rel, data):
    p = os.path.join(stage, "assets", "minecraft", "textures", rel + ".mcmeta")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data)


def save_img(stage, rel, img):
    p = os.path.join(stage, "assets", "minecraft", "textures", rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    img.save(p)
    print(f"    + {rel}")


def write_mcmeta(stage, desc):
    with open(os.path.join(stage, "pack.mcmeta"), "w", encoding="utf-8") as f:
        json.dump({"pack": {"pack_format": PACK_FORMAT, "description": desc}}, f, indent=2)


def font(sz, bold=True):
    names = (["arialbd.ttf", "segoeuib.ttf"] if bold else []) + ["arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]
    for n in names:
        try:
            return ImageFont.truetype(n, sz)
        except Exception:
            continue
    return ImageFont.load_default()


def zip_dir(stage, zip_path):
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(stage):
            for fn in files:
                full = os.path.join(root, fn)
                z.write(full, os.path.relpath(full, stage).replace("\\", "/"))
    print(f"    -> {os.path.basename(zip_path)} ({os.path.getsize(zip_path)} bytes)")


def tile(img, size):
    """Tile a small texture to fill size (nearest, keeps pixel art)."""
    w, h = img.size
    out = Image.new("RGBA", size)
    for y in range(0, size[1], h):
        for x in range(0, size[0], w):
            out.paste(img, (x, y))
    return out


def gallery_compare(out_path, left_label, left_img, right_label, right_img, caption=""):
    """800x800 before/after panel using real textures."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    W = 800
    g = Image.new("RGBA", (W, W), (10, 10, 12, 255))
    d = ImageDraw.Draw(g)
    half = W // 2
    panel = 300
    for img, cx, label in [(left_img, half // 2, left_label), (right_img, half + half // 2, right_label)]:
        im = img.convert("RGBA").resize((panel, panel), Image.NEAREST)
        g.paste(im, (cx - panel // 2, 150), im)
        d.rectangle([cx - panel // 2 - 2, 148, cx + panel // 2 + 1, 150 + panel], outline=(70, 74, 92), width=2)
        bar_w = panel
        x0 = cx - bar_w // 2
        d.rectangle([x0, 500, x0 + bar_w, 556], fill=(24, 24, 30, 255))
        f = font(30)
        tb = d.textbbox((0, 0), label, font=f)
        d.text((cx - (tb[2] - tb[0]) // 2, 528 - (tb[3] - tb[1]) // 2 - 6), label, fill=(255, 255, 255, 255), font=f)
    d.line([(half, 140), (half, 570)], fill=(60, 60, 70, 255), width=3)
    if caption:
        f = font(26, bold=False)
        tb = d.textbbox((0, 0), caption, font=f)
        d.text((W // 2 - (tb[2] - tb[0]) // 2, 640), caption, fill=(150, 155, 170, 255), font=f)
    g.convert("RGB").save(out_path)
    print(f"    + gallery {os.path.basename(out_path)}")


def make_icon(stage, tex, bg=(14, 14, 18)):
    """128x128 pack icon from a real texture."""
    d = Image.new("RGBA", (128, 128), bg + (255,))
    t = tex.convert("RGBA")
    side = 100
    t = t.resize((side, side), Image.NEAREST)
    d.paste(t, ((128 - side) // 2, (128 - side) // 2), t)
    d.save(os.path.join(stage, "pack.png"))
    print("    + pack.png")


def finish(slug, name, summary, body, gallery, version="1.0.0", game_versions=V_WIDE,
           extra_meta=None, changelog="Initial release."):
    """Zip the staged pack, copy artefacts, write manifest."""
    stage = os.path.join(BUILD, slug)
    zip_path = os.path.join(DIST, f"{slug}-{version}-resourcepack-1.21.4.zip")
    zip_dir(stage, zip_path)
    os.makedirs(os.path.join(PACKS, slug, "files"), exist_ok=True)
    shutil.copy2(zip_path, os.path.join(PACKS, slug, "files", os.path.basename(zip_path)))
    shutil.copy2(os.path.join(stage, "pack.png"), os.path.join(PACKS, slug, "icon.png"))
    manifest = {
        "slug": slug,
        "name": name,
        "project_type": "resourcepack",
        "summary": summary,
        "body": body,
        "license": "All Rights Reserved",
        "categories": ["utility", "16x"],
        "curseforge_id": None,
        "modrinth_id": None,
        "links": {"website_url": CF_MEMBER, "source_url": None, "issues_url": None, "wiki_url": ""},
        "version": {
            "number": version, "type": "release", "changelog": changelog,
            "loaders": ["minecraft"], "game_versions": game_versions,
        },
        "file": os.path.basename(zip_path),
        "icon": "icon.png",
        "gallery": gallery,
    }
    if extra_meta:
        manifest.update(extra_meta)
    with open(os.path.join(PACKS, slug, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print("    + manifest.json")


def funnel_body(intro, bullets, title_cf=CF_FLAGSHIP):
    """Standard body: intro + bullets + funnel to the flagship bundle."""
    return (intro + "\\n\\n" + bullets +
            "\\n\\n---\\n\\n### 🚀 Want everything in one pack?\\n"
            "This feature is part of **[PvP Essentials](" + CF_FLAGSHIP + ")** — the all-in-one pack with "
            "crosshair, visible ores, short sword, low fire and clear pumpkin.\\n"
            "> 💡 **CurseForge is the source of truth** — the most up-to-date, bug-free versions land there first: "
            "[Fliflight on CurseForge](" + CF_MEMBER + ")")


def fresh(slug, subdirs):
    stage = os.path.join(BUILD, slug)
    if os.path.isdir(stage):
        shutil.rmtree(stage)
    for sub in subdirs:
        os.makedirs(os.path.join(stage, sub), exist_ok=True)
    return stage


# ================================================================ 1. LOW SHIELD
print("=" * 62); print("[1] fliflight-low-shield")
slug = "fliflight-low-shield"
stage = fresh(slug, ["assets/minecraft/models/item"])
shield_model = {
    "gui_light": "front",
    "textures": {"particle": "block/dark_oak_planks"},
    "display": {
        "thirdperson_righthand": {"rotation": [0, 90, 0], "translation": [10, 6, -4], "scale": [1, 1, 1]},
        "thirdperson_lefthand":  {"rotation": [0, 90, 0], "translation": [10, 6, 12], "scale": [1, 1, 1]},
        "firstperson_righthand": {"rotation": [0, 180, 5], "translation": [-10, -1, -10], "scale": [0.7, 0.7, 0.7]},
        "firstperson_lefthand":  {"rotation": [0, 180, 5], "translation": [10, -3, -10], "scale": [0.7, 0.7, 0.7]},
        "gui":    {"rotation": [15, -25, -5], "translation": [2, 3, 0], "scale": [0.65, 0.65, 0.65]},
        "fixed":  {"rotation": [0, 180, 0], "translation": [-4.5, 4.5, -5], "scale": [0.55, 0.55, 0.55]},
        "ground": {"rotation": [0, 0, 0], "translation": [2, 4, 2], "scale": [0.25, 0.25, 0.25]},
    },
}
p = os.path.join(stage, "assets", "minecraft", "models", "item", "shield.json")
with open(p, "w", encoding="utf-8") as f:
    json.dump(shield_model, f, indent=4)
print("    + models/item/shield.json (first-person scale 1.25 -> 0.7, lowered)")
write_mcmeta(stage, "Low Shield - the shield no longer covers your view")

shield_tex = vimg("entity/shield_base.png")
make_icon(stage, shield_tex)

# gallery: first-person mock (big vs small shield)
bg = tile(vimg("block/dark_oak_planks.png"), (300, 300))
def fp_view(scale):
    base = bg.copy()
    sh = shield_tex.resize((int(150 * scale), int(150 * scale)), Image.NEAREST)
    base.alpha_composite(sh, (150 - sh.size[0] // 2, 300 - sh.size[1] + int(40 * scale)))
    return base
gallery_compare(os.path.join(PACKS, slug, "gallery", "01_shield.png"),
                "Vanilla", fp_view(1.25), "Low Shield", fp_view(0.7),
                "First-person view: the shield sits lower and smaller")
finish(slug, "Low Shield — Shield Out of the Way",
       "Makes the first-person shield smaller and lower so it never blocks your view in PvP.",
       funnel_body(
           "The vanilla shield covers a huge chunk of your screen when held. This pack **shrinks it and lowers it** so you keep full visibility while staying protected.",
           "- 🛡️ **Smaller shield** — 45% smaller in first person\\n- ⬇️ **Sits lower** — out of your line of sight\\n- ✅ **Works on every launcher** — just drop in `resourcepacks` and enable"),
       ["01_shield.png"],
       changelog="Initial release: smaller, lowered first-person shield.")

# ================================================================ 2. NO VIGNETTE
print("=" * 62); print("[2] fliflight-no-vignette")
slug = "fliflight-no-vignette"
stage = fresh(slug, ["assets/minecraft/textures/misc"])
vig = vimg("misc/vignette.png")
w, h = vig.size
# vanilla: dark at the edges, bright in the middle. Fill uniformly with the CENTRE value
# (= the value the vanilla vignette shows where there is no darkening) -> no darkening anywhere.
cx, cy = w // 2, h // 2
centre = vig.getpixel((cx, cy))
flat = Image.new(vig.mode, (w, h), centre)
save_img(stage, "misc/vignette.png", flat)
save_meta(stage, "misc/vignette", vmeta("misc/vignette.png"))
print("    + misc/vignette.png.mcmeta")
write_mcmeta(stage, "No Vignette - no more dark corners")
make_icon(stage, Image.new("RGBA", (16, 16), (24, 26, 34, 255)))

# gallery: stone screen darkened at the edges vs uniform
stone = tile(vimg("block/stone.png"), (300, 300))
def vignetted():
    b = stone.copy()
    ov = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    for r in range(150, 0, -3):
        a = int(200 * (1 - r / 150.0) ** 2)     # darker towards the corners
        dd.ellipse([150 - r * 1.15, 150 - r * 1.15, 150 + r * 1.15, 150 + r * 1.15], outline=(0, 0, 0, a), width=4)
    b.alpha_composite(ov)
    return b
gallery_compare(os.path.join(PACKS, slug, "gallery", "01_vignette.png"),
                "Vanilla", vignetted(), "No Vignette", stone,
                "The dark corners are gone - clearer view, day and night")
finish(slug, "No Vignette — Clear Screen Corners",
       "Removes the dark corner shading so the whole screen stays evenly lit.",
       funnel_body(
           "Vanilla darkens the corners of your screen with a vignette. This pack **removes it completely** for a cleaner, brighter view.",
           "- 🌓 **No more dark corners** — the whole screen is evenly clear\\n- 👀 **Better awareness** in dark caves and at night\\n- ✅ **Works on every launcher** — just drop in `resourcepacks` and enable"),
       ["01_vignette.png"],
       changelog="Initial release: removes the vignette overlay.")

# ================================================================ 3. CLEAR WATER
print("=" * 62); print("[3] fliflight-clear-water")
slug = "fliflight-clear-water"
stage = fresh(slug, ["assets/minecraft/textures/block", "assets/minecraft/textures/misc"])
def fade_alpha(img, factor):
    img = img.convert("RGBA")
    px = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, int(a * factor))
    return img

for name in ["water_still", "water_flow"]:
    src = vimg(f"block/{name}.png")
    save_img(stage, f"block/{name}.png", fade_alpha(src, 0.42))
    save_meta(stage, f"block/{name}", vmeta(f"block/{name}.png"))
    print(f"    + block/{name}.png.mcmeta")

save_img(stage, "block/water_overlay.png", Image.new("RGBA", (16, 16), (0, 0, 0, 0)))
under = vimg("misc/underwater.png")
save_img(stage, "misc/underwater.png", Image.new("RGBA", under.size, (0, 0, 0, 0)))
write_mcmeta(stage, "Clear Water - see through water and underwater")
make_icon(stage, vimg("block/water_still.png").crop((0, 0, 16, 16)))

# gallery: stone seabed + opaque vs transparent water layer
seabed = tile(vimg("block/sand.png"), (300, 300))
def watery(alpha):
    b = seabed.copy()
    ov = Image.new("RGBA", (300, 300), (48, 92, 200, alpha))
    b.alpha_composite(ov)
    return b
gallery_compare(os.path.join(PACKS, slug, "gallery", "01_water.png"),
                "Vanilla", watery(190), "Clear Water", watery(38),
                "Opaque water vs clear water - the seabed stays visible")
finish(slug, "Clear Water — See Through Water",
       "Makes water translucent so you can see the seabed, mobs and structures while swimming.",
       funnel_body(
           "Water in vanilla hides everything under the surface. This pack makes it **see-through**, above and below.",
           "- 🌊 **Translucent water** — spot mobs, ores and temples while swimming\\n- 🐟 **Clear underwater view** — the blue screen overlay is removed\\n- ✅ **Works on every launcher** — just drop in `resourcepacks` and enable"),
       ["01_water.png"],
       changelog="Initial release: translucent water + clear underwater overlay.")

# ================================================================ 4. CLEAR LAVA
print("=" * 62); print("[4] fliflight-clear-lava")
slug = "fliflight-clear-lava"
stage = fresh(slug, ["assets/minecraft/textures/block"])
for name in ["lava_still", "lava_flow"]:
    src = vimg(f"block/{name}.png")
    save_img(stage, f"block/{name}.png", fade_alpha(src, 0.5))
    save_meta(stage, f"block/{name}", vmeta(f"block/{name}.png"))
    print(f"    + block/{name}.png.mcmeta")
write_mcmeta(stage, "Clear Lava - see through lava")
make_icon(stage, vimg("block/lava_still.png").crop((0, 0, 16, 16)))
nether = tile(vimg("block/netherrack.png"), (300, 300))
def lava_layer(alpha):
    b = nether.copy()
    ov = Image.new("RGBA", (300, 300), (207, 92, 16, alpha))
    b.alpha_composite(ov)
    return b
gallery_compare(os.path.join(PACKS, slug, "gallery", "01_lava.png"),
                "Vanilla", lava_layer(255), "Clear Lava", lava_layer(110),
                "Solid lava vs clear lava - see what is underneath")
finish(slug, "Clear Lava — See Through Lava",
       "Makes lava semi-transparent so you can see what is underneath before you take the plunge.",
       funnel_body(
           "Vanilla lava is a solid orange wall — you never know what is below. This pack makes it **see-through**.",
           "- 🌋 **Translucent lava** — see terrain and mobs under the surface\\n- 🧭 **Safer nether travel** — spot drops before crossing\\n- ✅ **Works on every launcher** — just drop in `resourcepacks` and enable"),
       ["01_lava.png"],
       changelog="Initial release: semi-transparent lava.")

# ================================================================ 5. CLEAR SPYGLASS
print("=" * 62); print("[5] fliflight-clear-spyglass")
slug = "fliflight-clear-spyglass"
stage = fresh(slug, ["assets/minecraft/textures/misc"])
scope = vimg("misc/spyglass_scope.png")
save_img(stage, "misc/spyglass_scope.png", Image.new("RGBA", scope.size, (0, 0, 0, 0)))
write_mcmeta(stage, "Clear Spyglass - no scope overlay")
# icon: the spyglass item texture is not a thing; use a simple scope glyph
ic = Image.new("RGBA", (128, 128), (14, 14, 18, 255))
idd = ImageDraw.Draw(ic)
idd.ellipse([28, 28, 100, 100], outline=(200, 205, 220, 255), width=6)
idd.line([(64, 34), (64, 94)], fill=(120, 190, 255, 255), width=3)
idd.line([(34, 64), (94, 64)], fill=(120, 190, 255, 255), width=3)
ic.save(os.path.join(stage, "pack.png"))
print("    + pack.png")
scenery = tile(vimg("block/grass_block_side.png"), (300, 300))
masked = scenery.copy()
masked.alpha_composite(Image.new("RGBA", (300, 300), (0, 0, 0, 215)).resize((300, 300)))
ddm = ImageDraw.Draw(masked)
ddm.ellipse([70, 70, 230, 230], fill=(0, 0, 0, 0))
masked = Image.composite(scenery, masked, Image.new("L", (300, 300), 0))
# rebuild properly: circular hole
masked = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
masked.paste(Image.new("RGBA", (300, 300), (0, 0, 0, 215)), (0, 0))
hole = Image.new("L", (300, 300), 255)
ImageDraw.Draw(hole).ellipse([70, 70, 230, 230], fill=0)
masked.putalpha(Image.composite(Image.new("L", (300, 300), 215), Image.new("L", (300, 300), 0), hole))
view = scenery.copy(); view.alpha_composite(masked)
gallery_compare(os.path.join(PACKS, slug, "gallery", "01_spyglass.png"),
                "Vanilla", view, "Clear Spyglass", scenery,
                "Scope overlay removed - full clear view while zoomed")
finish(slug, "Clear Spyglass — No Scope Overlay",
       "Removes the black spyglass overlay so you get a full clear view while zoomed in.",
       funnel_body(
           "The vanilla spyglass blocks most of your view with a black scope. This pack **removes the overlay** so the whole screen stays usable.",
           "- 🔭 **No scope overlay** — zoom with full peripheral vision\\n- 🎯 **Better spotting** — find players and bases from far away\\n- ✅ **Works on every launcher** — just drop in `resourcepacks` and enable"),
       ["01_spyglass.png"],
       changelog="Initial release: spyglass scope overlay removed.")

# ================================================================ 6. CLEAN HOTBAR
print("=" * 62); print("[6] fliflight-clean-hotbar")
slug = "fliflight-clean-hotbar"
stage = fresh(slug, ["assets/minecraft/textures/gui/sprites/hud"])
HW, HH = 182, 22
bar = Image.new("RGBA", (HW, HH), (0, 0, 0, 0))
dr = ImageDraw.Draw(bar)
slot = 20
pad = 1
for i in range(9):
    x0 = pad + i * slot
    dr.rectangle([x0, pad, x0 + slot - 2, HH - pad - 1], fill=(12, 12, 16, 170), outline=(90, 94, 110, 210))
bar.save(os.path.join(stage, "assets/minecraft/textures/gui/sprites/hud/hotbar.png"))
print("    + gui/sprites/hud/hotbar.png")

sel = Image.new("RGBA", (24, 23), (0, 0, 0, 0))
ds = ImageDraw.Draw(sel)
ds.rectangle([0, 0, 23, 22], outline=(255, 255, 255, 235), width=2)
ds.rectangle([2, 2, 21, 20], outline=(255, 255, 255, 90), width=1)
sel.save(os.path.join(stage, "assets/minecraft/textures/gui/sprites/hud/hotbar_selection.png"))
print("    + gui/sprites/hud/hotbar_selection.png")

xpbg = Image.new("RGBA", (182, 5), (16, 16, 20, 215))
xpbg.save(os.path.join(stage, "assets/minecraft/textures/gui/sprites/hud/experience_bar_background.png"))
xp = Image.new("RGBA", (182, 5), (110, 230, 90, 245))
xp.save(os.path.join(stage, "assets/minecraft/textures/gui/sprites/hud/experience_bar_progress.png"))
print("    + experience_bar background + progress")
write_mcmeta(stage, "Clean Hotbar - flat, clean hotbar and XP bar")
make_icon(stage, bar)

vh = vimg("gui/sprites/hud/hotbar.png").resize((300, 36), Image.NEAREST)
ch = bar.resize((300, 36), Image.NEAREST)
canvas_v = Image.new("RGBA", (300, 300), (10, 10, 12, 255)); canvas_v.paste(vh, (0, 132), vh)
canvas_c = Image.new("RGBA", (300, 300), (10, 10, 12, 255)); canvas_c.paste(ch, (0, 132), ch)
gallery_compare(os.path.join(PACKS, slug, "gallery", "01_hotbar.png"),
                "Vanilla", canvas_v, "Clean Hotbar", canvas_c,
                "Flat, minimal hotbar - same 9 slots, less clutter")
finish(slug, "Clean Hotbar — Flat Minimal HUD",
       "Replaces the busy vanilla hotbar with a flat, clean design and a clearer XP bar.",
       funnel_body(
           "The vanilla hotbar is thick and over-detailed. This pack uses a **flat, minimal design** with a clearer XP bar.",
           "- 🎨 **Flat clean design** — less visual noise, same 9 slots\\n- 📊 **Clearer XP bar** — bright green, easy to read at a glance\\n- ✅ **Works on every launcher** — just drop in `resourcepacks` and enable"),
       ["01_hotbar.png"],
       game_versions=V_MODERN,
       changelog="Initial release: flat clean hotbar + XP bar.")

# ================================================================ 7. THIN TOTEM
print("=" * 62); print("[7] fliflight-thin-totem")
slug = "fliflight-thin-totem"
stage = fresh(slug, ["assets/minecraft/textures/item"])
tot = vimg("item/totem_of_undying.png")
thin = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
small = tot.resize((7, 16), Image.LANCZOS)
thin.paste(small, (4, 0), small)
save_img(stage, "item/totem_of_undying.png", thin)
write_mcmeta(stage, "Thin Totem - the totem pop animation no longer blocks your view")
make_icon(stage, tot)
gallery_compare(os.path.join(PACKS, slug, "gallery", "01_totem.png"),
                "Vanilla", tot.resize((256, 256), Image.NEAREST), "Thin Totem", thin.resize((256, 256), Image.NEAREST),
                "Slimmer totem - the pop animation covers far less of the screen")
finish(slug, "Thin Totem — Slimmer Totem Pop",
       "Slims down the totem of undying so its pop animation no longer blocks your view mid-fight.",
       funnel_body(
           "Pop a totem in a fight and the vanilla animation covers a big part of your screen. This pack makes the totem **thinner**.",
           "- 🪶 **Thin totem** — far less screen coverage when it pops\\n- ⚔️ **Stay in the fight** — keep track of your opponent\\n- ✅ **Works on every launcher** — just drop in `resourcepacks` and enable"),
       ["01_totem.png"],
       changelog="Initial release: thinner totem texture.")

# ================================================================ 8. CLEAR POWDER SNOW
print("=" * 62); print("[8] fliflight-clear-powder-snow")
slug = "fliflight-clear-powder-snow"
stage = fresh(slug, ["assets/minecraft/textures/misc"])
pso = vimg("misc/powder_snow_outline.png")
save_img(stage, "misc/powder_snow_outline.png", Image.new("RGBA", pso.size, (0, 0, 0, 0)))
write_mcmeta(stage, "Clear Powder Snow - no frost overlay when freezing")
make_icon(stage, Image.new("RGBA", (128, 128), (14, 14, 18, 255)))
snow = tile(vimg("block/snow.png"), (300, 300))
def frosted():
    b = snow.copy()
    ov = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    dd2 = ImageDraw.Draw(ov)
    for r in range(150, 0, -3):
        a = int(170 * (1 - r / 150.0) ** 2)
        dd2.ellipse([150 - r * 1.15, 150 - r * 1.15, 150 + r * 1.15, 150 + r * 1.15], outline=(225, 240, 255, a), width=4)
    b.alpha_composite(ov)
    return b
gallery_compare(os.path.join(PACKS, slug, "gallery", "01_powder_snow.png"),
                "Vanilla", frosted(), "Clear Powder Snow", snow,
                "Frost overlay removed - clear vision while freezing")
finish(slug, "Clear Powder Snow — No Frost Overlay",
       "Removes the frost screen overlay so you can see clearly while freezing in powder snow.",
       funnel_body(
           "Freezing in powder snow covers your screen with a frost overlay. This pack **removes it** so you can see where you are going.",
           "- ❄️ **No frost overlay** — full clear vision while freezing\\n- 🏔️ **Survive powder snow** — spot the exit and your way out\\n- ✅ **Works on every launcher** — just drop in `resourcepacks` and enable"),
       ["01_powder_snow.png"],
       changelog="Initial release: frost overlay removed.")

print("\n" + "=" * 62)
print("ALL 8 PACKS BUILT")
