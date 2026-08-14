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

TEXTURE_MAP = {
    "assets/minecraft/textures/block/": "textures/blocks/",
    "assets/minecraft/textures/item/": "textures/items/",
    "assets/minecraft/textures/entity/": "textures/entity/",
    "assets/minecraft/textures/gui/": "textures/ui/",
    "assets/minecraft/textures/misc/": "textures/misc/",
    "assets/minecraft/textures/particle/": "textures/particle/",
}


def build(java_zip, out_mcpack, name, description="", icon_png=None):
    tmp = tempfile.mkdtemp()
    copied = 0
    with zipfile.ZipFile(java_zip) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            for src, dst in TEXTURE_MAP.items():
                if info.filename.startswith(src):
                    out = os.path.join(tmp, dst, os.path.relpath(info.filename, src))
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    with open(out, "wb") as f:
                        f.write(z.read(info))
                    copied += 1
                    break

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

    with zipfile.ZipFile(out_mcpack) as z:
        files = sorted(n for n in z.namelist() if not n.endswith("/"))
    print(f"[mcpack] {out_mcpack}  ({copied} textures mapped, {len(files)} files)")
    for n in files:
        print(f"    {n}")
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--description", default="")
    ap.add_argument("--icon", default=None)
    a = ap.parse_args()
    build(a.zip, a.out, a.name, a.description, a.icon)
