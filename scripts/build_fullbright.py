#!/usr/bin/env python3
"""Build the Fliflight "Everlight" resource pack — see in the dark, everywhere.

WHY a loader is needed: the light map is NOT a vanilla asset. Verified against the 1.21.4
client jar, which ships only the shader that GENERATES it
(assets/minecraft/shaders/core/lightmap.fsh). Overriding it requires OptiFine — or Polytone.

Two targets are shipped so the pack is not limited to OptiFine users:
  OptiFine : assets/minecraft/optifine/lightmap/world0.png / world-1.png / world1.png
  Polytone : assets/minecraft/polytone/lightmaps/overworld.png / the_nether.png / the_end.png
             (+ a small .json beside each) — Polytone is the Fabric/NeoForge mod that exposes
             OptiFine-style light maps to Iris/Sodium players.

Format, from the official docs (optifine.readthedocs.io/custom_lightmaps.html) and confirmed
against a working third-party pack (16x64, identical paths), so the shape is known-good:
  any WIDTH, height 32 — or 64 to also override night vision.
  32 tall : rows 0-15 the sunlight axis (far left night, far right day, lightning at the end),
            rows 16-31 the torchlight axis.
  64 tall : rows 32-47 and 48-63 repeat those two axes, used while night vision is active.
  Torchlight x is a random FLICKER value, so one identical colour across a row = no flicker.
  Nether and End have no day/night cycle: give their sun band one flat colour across the width.

Why this layout is deliberately orientation-proof:
  - the torch band is a single flat colour (no flicker, and the direction of its level axis
    cannot matter)
  - the sun band is flat VERTICALLY, so the direction of the level axis inside the band cannot
    matter either; only the documented night->day horizontal ramp is used
  - every band stays bright, so whichever rule the loader uses to combine sun and torch
    (add, max, multiply) the result is still clearly lit. Night is ~80% of day rather than
    equal to it, so the world keeps a day/night feel instead of looking permanently noon.

Run:  python scripts/build_fullbright.py
"""
import io
import json
import os
import shutil
import zipfile

from PIL import Image, ImageDraw, ImageFilter

BASE = r"C:\Users\user\fliflight-mods"
PACKS = os.path.join(BASE, "packs")
BUILD = os.path.join(BASE, "build")
JAR = os.path.join(BUILD, "client-1.21.4.jar")

SLUG = "fliflight-everlight"
NAME = "Everlight - See in the Dark"
PACK_FORMAT = 46
WIDTH = 16          # the shape proven by a working third-party pack found in the user's folder
HEIGHT = 64         # 64 = the night-vision palettes are supplied too (32 would cover plain play)

# Polytone mirrors OptiFine's light map under its own dimension names
POLYTONE = {"world0": "overworld", "world-1": "the_nether", "world1": "the_end"}
POLYTONE_JSON = {"lightning_strike_columns": False}   # same key as the working reference pack

V_WIDE = ["1.19", "1.19.2", "1.19.4", "1.20", "1.20.1", "1.20.2", "1.20.4", "1.20.5", "1.20.6",
          "1.21", "1.21.1", "1.21.3", "1.21.4", "1.21.5", "1.21.6", "1.21.7", "1.21.8"]

# --- colours ---------------------------------------------------------------
# Night is intentionally NOT the same as day: keeping a ~20% difference preserves the
# day/night feel while never being dark enough to hide anything.
NIGHT = (206, 212, 236)      # bright, faintly cool so night still reads as night
DAY = (255, 255, 255)
TORCH = (255, 249, 240)      # warm, identical on every pixel of a row => zero flicker
NETHER_AMBIENT = (255, 249, 244)
END_AMBIENT = (250, 250, 255)

BG = (13, 14, 18)            # house style: flat near-black backdrop


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sun_row(t):
    """t = 0 far left (night) -> 1 far right (lightning)."""

    def smooth(x):
        x = max(0.0, min(1.0, x))
        return x * x * (3 - 2 * x)

    if t < 0.10:
        return NIGHT
    if t < 0.55:                                   # night -> day (dawn)
        return lerp(NIGHT, DAY, smooth((t - 0.10) / 0.45))
    return DAY                                     # already at maximum: lightning adds nothing


def palette(flat_ambient=None):
    """rows 0-15 sun, 16-31 torch, 32-47 night-vision sun, 48-63 night-vision torch."""
    img = Image.new("RGB", (WIDTH, HEIGHT))
    px = img.load()
    for y in range(HEIGHT):
        band, nv = y % 32, y >= 32
        for x in range(WIDTH):
            if band < 16:                          # sun axis
                if flat_ambient is not None:       # Nether / End: no day-night cycle
                    px[x, y] = flat_ambient
                elif nv:
                    px[x, y] = DAY                 # with night vision: flat maximum
                else:
                    px[x, y] = sun_row(x / (WIDTH - 1))
            else:                                  # torch axis: flat => no flicker
                px[x, y] = TORCH
    return img


def vanilla_bytes(rel):
    with zipfile.ZipFile(JAR) as z:
        return z.read("assets/minecraft/textures/" + rel)


def item_texture(candidates):
    for c in candidates:
        try:
            return Image.open(io.BytesIO(vanilla_bytes(c))).convert("RGBA"), c
        except KeyError:
            continue
    raise SystemExit("aucune texture d'item trouvee parmi " + ", ".join(candidates))


def build_icon(size):
    """Icon art: the user's own torch logo, cropped to the flame and shaft.

    The full logo is a round badge carrying the "EVERLIGHT" lettering plus a subtitle; keeping
    it whole made the text unreadable noise at 32 px, and cropping just below it cut the torch.
    This crop keeps the flame clear of the top edge (measured: ~7% headroom) and excludes every
    letter — checked by looking at the render at 32/64/128 px, not assumed. Falls back to a
    generated item render if the source art is missing.
    """
    ICON_SOURCE = os.path.join(BASE, "packs", SLUG, "icon-source.jpg")
    ICON_CROP = (0.46, 0.34)          # (side as a fraction of width, vertical centre)
    if os.path.exists(ICON_SOURCE):
        art = Image.open(ICON_SOURCE).convert("RGB")
        w0, h0 = art.size
        s = int(w0 * ICON_CROP[0])
        cx, cy = w0 // 2, int(h0 * ICON_CROP[1])
        art = art.crop((cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2))
        art = art.resize((size, size), Image.LANCZOS)
        print(f"    icone {size}x{size} (logo torche, recadre {ICON_CROP})")
        return art

    """Flat dark backdrop + a tight warm glow + the item. Deliberately NOT a wide halo:
    a large concentric glow reads as a muddy dome once the icon is shown at 32 px."""
    img = Image.new("RGB", (size, size), BG)
    item, src = item_texture(["item/lantern.png", "block/glowstone.png", "item/glowstone_dust.png",
                              "block/lantern.png", "block/torch.png"])
    # The vanilla texture is 16x16 with transparent PADDING: crop to the drawn pixels first.
    # Scaling the padded canvas left the artwork filling ~15% of the frame, which reads as a
    # lone spark at 32 px (confirmed by looking at the render, not assumed).
    bbox = item.getbbox()
    if bbox:
        item = item.crop(bbox)
    scale = max(1, int(size * 0.78) // max(item.size))   # integer scaling keeps pixels crisp
    iw, ih = item.size[0] * scale, item.size[1] * scale
    off = ((size - iw) // 2, (size - ih) // 2)

    # glow: soft, tight, just around the item
    glow = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(glow)
    pad = int(max(iw, ih) * 0.18)
    d.rounded_rectangle([off[0] - pad, off[1] - pad, off[0] + iw + pad, off[1] + ih + pad],
                        radius=int(max(iw, ih) * 0.34), fill=100)
    glow = glow.filter(ImageFilter.GaussianBlur(radius=max(2, max(iw, ih) // 14)))
    warm = Image.new("RGB", (size, size), (255, 196, 110))
    img = Image.blend(img, Image.composite(warm, img, glow), 0.45)

    item = item.resize((iw, ih), Image.NEAREST)
    img.paste(item, off, item)
    print(f"    icone {size}x{size} (item {src} {iw}x{ih}, echelle x{scale})")
    return img


def stage():
    st = os.path.join(BUILD, SLUG)
    if os.path.isdir(st):
        shutil.rmtree(st)
    of = os.path.join(st, "assets", "minecraft", "optifine", "lightmap")
    po = os.path.join(st, "assets", "minecraft", "polytone", "lightmaps")
    os.makedirs(of, exist_ok=True)
    os.makedirs(po, exist_ok=True)

    for nom, flat in (("world0", None), ("world-1", NETHER_AMBIENT), ("world1", END_AMBIENT)):
        img = palette(flat)
        img.save(os.path.join(of, nom + ".png"))
        img.save(os.path.join(po, POLYTONE[nom] + ".png"))
        with open(os.path.join(po, POLYTONE[nom] + ".json"), "w", encoding="utf-8") as f:
            json.dump(POLYTONE_JSON, f)
        print(f"    + optifine/lightmap/{nom}.png  + polytone/lightmaps/{POLYTONE[nom]}.png"
              f"  {WIDTH}x{HEIGHT}")

    with open(os.path.join(st, "pack.mcmeta"), "w", encoding="utf-8") as f:
        json.dump({"pack": {"pack_format": PACK_FORMAT,
                            "description": f"{NAME} - clear sight everywhere (OptiFine or Polytone)"}},
                  f, indent=2, ensure_ascii=False)

    build_icon(128).save(os.path.join(st, "pack.png"))
    return st


def ship(st):
    out = os.path.join(PACKS, SLUG)
    os.makedirs(os.path.join(out, "files"), exist_ok=True)
    os.makedirs(os.path.join(out, "gallery"), exist_ok=True)

    zipname = f"{SLUG}-1.0.0-resourcepack-1.21.4.zip"
    zpath = os.path.join(out, "files", zipname)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, names in os.walk(st):
            for n in names:
                full = os.path.join(root, n)
                z.write(full, os.path.relpath(full, st))
    print(f"    + files/{zipname}  ({os.path.getsize(zpath)} octets)")

    shutil.copy(os.path.join(st, "pack.png"), os.path.join(out, "pack.png"))
    build_icon(512).save(os.path.join(out, "icon.png"))

    man = {
        "slug": SLUG,
        "name": NAME,
        "project_type": "resourcepack",
        "summary": ("Brightens the light map so you always see clearly - caves, the Nether and "
                    "the End included. Works with OptiFine or Polytone."),
        "body": (
            f"**{NAME}** is a client-side resource pack for Minecraft Java Edition. It makes the "
            "world readable everywhere, and changes nothing else.\n\n"
            "### What it does\n"
            "- Replaces the light map, so low light levels stay bright instead of fading to black\n"
            "- Caves and the night surface become as readable as a sunlit plain - that is where\n"
            "  vanilla is genuinely black, and where this pack does the most\n"
            "- The Nether and the End get a lift as well, but vanilla already lights them\n"
            "  reasonably well, so the difference there is smaller\n"
            "- Torch light is perfectly steady - no flicker at all\n"
            "- Night stays slightly cooler and dimmer than day, so the world keeps a day/night "
            "cycle instead of looking permanently noon\n\n"
            "### Requirements - pick one\n"
            "- **OptiFine** (any recent version) - the classic route.\n"
            "- **Polytone** - a small Fabric/NeoForge mod that adds this feature for players "
            "running Sodium and Iris instead.\n\n"
            "The light map is not a vanilla asset - Minecraft generates it at runtime - so one of "
            "the two is genuinely required. Without either, this pack will do nothing.\n\n"
            "### Install\n"
            "1. Install **OptiFine**, or **Polytone** on Fabric/NeoForge.\n"
            "2. Download the `.zip` from this page (do not unzip it).\n"
            "3. Drop it into `.minecraft/resourcepacks` and enable it in "
            "**Options -> Resource Packs**.\n\n"
            "Works on Minecraft **1.19 -> 1.21.x** (Java Edition). Client-side only: it works on "
            "any server, and no one else needs it.\n\n"
            "### Servers\n"
            "On competitive servers this is a visual advantage, so check the rules before using it.\n\n"
            "---\n\n"
            "Liked it? You can support the work on [Ko-fi](https://ko-fi.com/fliflight)."),
        "license": "All Rights Reserved",
        "categories": ["utility", "16x"],
        "curseforge_id": None,
        "modrinth_id": None,
        "links": {"website_url": "https://www.curseforge.com/members/fliflightmc/projects",
                  "source_url": None, "issues_url": None, "wiki_url": ""},
        "version": {"number": "1.0.0", "type": "release",
                    "changelog": "Initial release: bright light map for all three dimensions, "
                                 "flicker-free torch light, day/night kept readable. Ships light "
                                 "maps for both OptiFine and Polytone.",
                    "loaders": ["minecraft"], "game_versions": V_WIDE},
        "file": zipname, "icon": "icon.png",
        # the gallery IS whatever is on disk, so the manifest cannot drift from the listing
        "gallery": sorted(f for f in os.listdir(os.path.join(out, "gallery"))
                          if f.endswith(".png")),
        "cf_slug": "everlight-see-in-the-dark",
    }
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, indent=2, ensure_ascii=False)
    print("    + manifest.json")
    return zpath


def verify(zpath):
    """Re-open what was shipped and prove the format is right."""
    print("\n=== VERIFICATION ===")
    ok = True
    attendus = ["pack.mcmeta", "pack.png"]
    attendus += [f"assets/minecraft/optifine/lightmap/{n}.png" for n in ("world0", "world-1", "world1")]
    for v in POLYTONE.values():
        attendus += [f"assets/minecraft/polytone/lightmaps/{v}.png",
                     f"assets/minecraft/polytone/lightmaps/{v}.json"]
    with zipfile.ZipFile(zpath) as z:
        noms = z.namelist()
        for a in attendus:
            present = a in noms
            ok &= present
            print(f"  {'OK ' if present else 'NON'}  {a}")
        for n in noms:
            if not n.endswith(".png") or "lightmap" not in n:
                continue
            im = Image.open(io.BytesIO(z.read(n)))
            px = im.load()
            w, h = im.size
            haut = h == HEIGHT
            torches = {" ".join(map(str, px[x, y])) for y in (16, 24, 30, 48, 56, 62)
                       for x in range(w)}
            vertical = all(len({px[x, y] for y in range(16)}) == 1 for x in range(w))
            mini = min(sum(px[x, y]) // 3 for y in range(h) for x in range(w))
            print(f"\n  {n}  ({w}x{h})")
            print(f"     hauteur {HEIGHT}             : {'oui' if haut else 'NON'}")
            print(f"     bandes torche uniformes : {len(torches)} couleur(s) -> "
                  f"{'zero scintillement' if len(torches) == 1 else 'SCINTILLE'}")
            print(f"     bande soleil uniforme en vertical : {'oui' if vertical else 'NON'}")
            print(f"     luminosite minimale     : {mini}/255 "
                  f"{'(jamais sombre)' if mini > 150 else '(TROP SOMBRE)'}")
            ok &= haut and len(torches) == 1 and vertical and mini > 150
    print(f"\n  RESULTAT : {'tout est conforme' if ok else 'PROBLEME DETECTE'}")
    return ok


def main():
    print(f"construction de {NAME}\n")
    st = stage()
    z = ship(st)
    verify(z)
    print(f"\nsource deroulee : build/{SLUG}/")
    print(f"livrable        : packs/{SLUG}/")


if __name__ == "__main__":
    main()
