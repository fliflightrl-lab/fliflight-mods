#!/usr/bin/env python3
"""Read the fire animation .mcmeta files (cache the jar to disk this time)."""
import os, io, zipfile, json
import requests

JAR_CACHE = r"C:\Users\user\fliflight-mods\build\client-1.21.4.jar"
os.makedirs(os.path.dirname(JAR_CACHE), exist_ok=True)

if not os.path.exists(JAR_CACHE):
    vj = requests.get("https://piston-meta.mojang.com/v1/packages/0b21a8ab01286cddb2ef3af7b441bbced7bedf5e/1.21.4.json", timeout=60).json()
    jar_url = vj["downloads"]["client"]["url"]
    r = requests.get(jar_url, timeout=600, stream=True)
    with open(JAR_CACHE, "wb") as f:
        for chunk in r.iter_content(1024 * 256):
            f.write(chunk)
    print("jar cached")

with zipfile.ZipFile(JAR_CACHE) as z:
    for fn in ["assets/minecraft/textures/block/fire_0.png.mcmeta",
               "assets/minecraft/textures/block/fire_1.png.mcmeta"]:
        raw = z.read(fn).decode("utf-8")
        print(f"\n=== {fn} ===")
        print(raw)
