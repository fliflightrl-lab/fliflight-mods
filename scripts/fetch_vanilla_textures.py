#!/usr/bin/env python3
"""Fetch exact vanilla Minecraft textures (barrier, pumpkin item, fire) from Mojang's official assets."""
import json, os
import requests

MC_VERSION = "1.21.4"
WANTED = [
    "minecraft/textures/block/barrier.png",      # red "no entry" overlay
    "minecraft/textures/item/pumpkin.png",        # pumpkin item
    "minecraft/textures/block/fire_0.png",        # flame (for low fire)
    "minecraft/textures/block/fire_1.png",        # flame layer 2
]

out_dir = r"C:\Users\user\fliflight-mods\packs\pvp-essentials\gallery_src\vanilla"
os.makedirs(out_dir, exist_ok=True)

# 1. version manifest
m = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest_v2.json", timeout=60).json()
ver = next(v for v in m["versions"] if v["id"] == MC_VERSION)
print(f"version {MC_VERSION} -> {ver['url']}")

# 2. version JSON -> asset index
vj = requests.get(ver["url"], timeout=60).json()
aidx_url = vj["assetIndex"]["url"]
print(f"asset index -> {aidx_url}")

# 3. asset index -> object hashes
ai = requests.get(aidx_url, timeout=60).json()
objects = ai["objects"]
print(f"asset index has {len(objects)} objects")

# 4. download wanted assets
for key in WANTED:
    if key not in objects:
        print(f"  MISSING in index: {key}")
        continue
    h = objects[key]["hash"]
    url = f"https://resources.download.minecraft.net/{h[:2]}/{h}"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    fn = os.path.basename(key)
    path = os.path.join(out_dir, fn)
    with open(path, "wb") as f:
        f.write(r.content)
    print(f"  {fn:16s} {len(r.content):>8} bytes  <- {url[:70]}")

print(f"\nvanilla textures saved to {out_dir}")
