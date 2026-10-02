#!/usr/bin/env python3
"""
Convert a Java resource-pack zip into a Bedrock .mcpack.

Maps Java texture paths -> Bedrock texture paths and generates a valid
pack manifest.json (random UUIDs). Builds a .mcpack (a zip renamed).

Usage:
  python3 scripts/build_mcpack.py \
      --zip packs/visible-ores-all-versions-and-netherite/files/visible_ores-1.0.0-resourcepack-.zip \
      --out dist/bedrock/visible-ores.mcpack \
      --name "Visible Ores" \
      --description "See every ore and netherite clearly" \
      --icon packs/visible-ores-all-versions-and-netherite/icon.png
"""
import argparse, json, os, shutil, tempfile, uuid, zipfile

PREFIX = "assets/minecraft/textures/"

# Not replaceable on Bedrock (handled by the engine, no equivalent texture)
DROP = {
    "misc/underwater.png",
    "misc/vignette.png",
    "misc/powder_snow_outline.png",
}

# Java name -> exact Bedrock path (verified against Mojang/bedrock-samples)
RENAME = {
    "item/totem_of_undying.png": "textures/items/totem.png",
    "misc/spyglass_scope.png": "textures/entity/spyglass.png",
}

PREFIXES = [
    ("item/", "textures/items/"),
    ("entity/", "textures/entity/"),
    ("gui/", "textures/ui/"),
    ("misc/", "textures/misc/"),
    ("particle/", "textures/particle/"),
]


def map_path(rel):
    """Java path (after PREFIX) -> Bedrock path, or None if unsupported."""
    if rel in DROP:
        return None
    if rel in RENAME:
        return RENAME[rel]
    if rel.startswith("block/"):
        rest = rel[len("block/"):]
        if rest.startswith("deepslate_"):
            return "textures/blocks/deepslate/" + rest
        return "textures/blocks/" + rest
    for jp, bp in PREFIXES:
        if rel.startswith(jp):
            return bp + rel[len(jp):]
    return None


def build(java_zip, out_mcpack, name, description="", icon_png=None, verbose=False):
    tmp = tempfile.mkdtemp()
    copied, dropped, flipbooks = 0, [], []
    with zipfile.ZipFile(java_zip) as z:
        names = z.namelist()
        mcmeta = {n for n in names if n.endswith(".png.mcmeta")}
        for n in names:
            if n.endswith("/") or not n.startswith(PREFIX) or n.endswith(".mcmeta"):
                continue
            bp = map_path(n[len(PREFIX):])
            if bp is None:
                dropped.append(n[len(PREFIX):])
                continue
            out = os.path.join(tmp, bp)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "wb") as f:
                f.write(z.read(n))
            copied += 1
            if n + ".mcmeta" in mcmeta:
                try:
                    meta = json.loads(z.read(n + ".mcmeta").decode("utf-8-sig"))
                    tpf = int(meta.get("animation", {}).get("frametime", 1))
                except Exception:
                    tpf = 1
                flipbooks.append({"flipbook_texture": os.path.splitext(bp)[0],
                                  "atlas_tile": os.path.splitext(os.path.basename(bp))[0],
                                  "ticks_per_frame": tpf})

    if flipbooks:
        os.makedirs(os.path.join(tmp, "textures"), exist_ok=True)
        with open(os.path.join(tmp, "textures", "flipbook_textures.json"), "w", encoding="utf-8") as f:
            json.dump(flipbooks, f, indent=2)

    manifest = {
        "format_version": 2,
        "header": {
            "name": name,
            "description": description,
            "uuid": str(uuid.uuid4()),
            "version": [1, 0, 0],
            "min_engine_version": [1, 20, 0],
        },
        "modules": [{"type": "resources", "uuid": str(uuid.uuid4()), "version": [1, 0, 0]}],
    }
    with open(os.path.join(tmp, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    if icon_png and os.path.exists(icon_png):
        shutil.copy(icon_png, os.path.join(tmp, "pack_icon.png"))

    os.makedirs(os.path.dirname(out_mcpack), exist_ok=True)
    with zipfile.ZipFile(out_mcpack, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(tmp):
            for fn in files:
                p = os.path.join(root, fn)
                z.write(p, os.path.relpath(p, tmp).replace(os.sep, "/"))

    print(f"[mcpack] {os.path.basename(out_mcpack)}  {copied} textures"
          + (f", {len(flipbooks)} animées" if flipbooks else "")
          + (f", {len(dropped)} ignorées" if dropped else ""))
    if dropped and verbose:
        for d in dropped:
            print(f"    drop {d}")
    return {"copied": copied, "dropped": dropped, "flipbooks": len(flipbooks)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--description", default="")
    ap.add_argument("--icon", default=None)
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    build(a.zip, a.out, a.name, a.description, a.icon, a.verbose)
