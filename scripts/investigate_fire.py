#!/usr/bin/env python3
"""Investigate the real fire textures + overlay mechanism in 1.21.4."""
import os, io, zipfile
import requests
from PIL import Image

# 1. dimensions of already-extracted fire textures
for d in [r"C:\Users\user\fliflight-mods\packs\pvp-essentials\vanilla_src",
          r"C:\Users\user\fliflight-mods\packs\pvp-essentials\gallery_src\vanilla"]:
    for fn in ["fire_0.png", "fire_1.png"]:
        p = os.path.join(d, fn)
        if os.path.exists(p):
            img = Image.open(p)
            print(f"{fn} @ {d.split(chr(92))[-2]} : {img.size} mode={img.mode}")

# 2. list ALL fire-related files in the jar (textures + mcmeta)
vj = requests.get("https://piston-meta.mojang.com/v1/packages/0b21a8ab01286cddb2ef3af7b441bbced7bedf5e/1.21.4.json", timeout=60).json()
jar_url = vj["downloads"]["client"]["url"]
r = requests.get(jar_url, timeout=600, stream=True)
buf = io.BytesIO()
for chunk in r.iter_content(1024 * 256):
    buf.write(chunk)
buf.seek(0)

with zipfile.ZipFile(buf) as z:
    print("\n=== all fire-related files in jar ===")
    for n in sorted(z.namelist()):
        if "fire" in n.lower() and ("texture" in n.lower() or ".mcmeta" in n):
            print(f"  {n}")
    # also check for the first-person overlay in misc/
    print("\n=== misc/ textures ===")
    for n in sorted(z.namelist()):
        if n.startswith("assets/minecraft/textures/misc/") and n.endswith(".png"):
            print(f"  {n}")
