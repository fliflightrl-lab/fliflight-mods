#!/usr/bin/env python3
"""Extract the remaining vanilla textures at their correct 1.21.4 paths (reuse cached jar)."""
import os, io, zipfile
import requests

out_dir = r"C:\Users\user\fliflight-mods\packs\pvp-essentials\gallery_src\vanilla"
WANTED = [
    "assets/minecraft/textures/item/barrier.png",      # red "no entry" sign
    "assets/minecraft/textures/block/pumpkin_side.png", # pumpkin (item visual)
    "assets/minecraft/textures/block/carved_pumpkin.png", # carved face
]

# re-download jar (stream, ~28MB)
vj = requests.get("https://piston-meta.mojang.com/v1/packages/0b21a8ab01286cddb2ef3af7b441bbced7bedf5e/1.21.4.json", timeout=60).json()
jar_url = vj["downloads"]["client"]["url"]
r = requests.get(jar_url, timeout=600, stream=True)
r.raise_for_status()
buf = io.BytesIO()
for chunk in r.iter_content(1024 * 256):
    buf.write(chunk)
buf.seek(0)

with zipfile.ZipFile(buf) as z:
    names = set(z.namelist())
    for w in WANTED:
        if w in names:
            data = z.read(w)
            fn = os.path.basename(w)
            # avoid overwriting fire_* ; keep distinct names
            with open(os.path.join(out_dir, fn), "wb") as f:
                f.write(data)
            print(f"  extracted {fn} ({len(data)} bytes)")
        else:
            print(f"  NOT FOUND: {w}")
print("done")
