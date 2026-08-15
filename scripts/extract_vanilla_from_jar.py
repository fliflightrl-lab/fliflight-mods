#!/usr/bin/env python3
"""Download the official 1.21.4 client jar and extract the vanilla textures we need."""
import json, os, io, zipfile
import requests

out_dir = r"C:\Users\user\fliflight-mods\packs\pvp-essentials\gallery_src\vanilla"
os.makedirs(out_dir, exist_ok=True)

WANTED = [
    "assets/minecraft/textures/block/barrier.png",
    "assets/minecraft/textures/item/pumpkin.png",
    "assets/minecraft/textures/block/fire_0.png",
    "assets/minecraft/textures/block/fire_1.png",
]

# version JSON -> client jar URL
vj = requests.get("https://piston-meta.mojang.com/v1/packages/0b21a8ab01286cddb2ef3af7b441bbced7bedf5e/1.21.4.json", timeout=60).json()
jar_url = vj["downloads"]["client"]["url"]
print(f"client jar: {jar_url[:90]}...")

# stream download
r = requests.get(jar_url, timeout=600, stream=True)
r.raise_for_status()
total = int(r.headers.get("content-length", 0))
print(f"downloading jar ({total/1e6:.1f} MB)...")

buf = io.BytesIO()
got = 0
for chunk in r.iter_content(1024 * 256):
    buf.write(chunk)
    got += len(chunk)
print(f"downloaded {got/1e6:.1f} MB")

buf.seek(0)
with zipfile.ZipFile(buf) as z:
    names = set(z.namelist())
    for w in WANTED:
        if w in names:
            data = z.read(w)
            fn = os.path.basename(w)
            with open(os.path.join(out_dir, fn), "wb") as f:
                f.write(data)
            print(f"  extracted {fn} ({len(data)} bytes)")
        else:
            print(f"  NOT FOUND in jar: {w}")
            # list similar
            base = os.path.basename(w)
            similar = [n for n in names if base.split('.')[0] in n and n.endswith('.png')]
            for s in similar[:10]:
                print(f"      similar: {s}")
