#!/usr/bin/env python3
"""Find the real asset-index keys for barrier/pumpkin/fire textures."""
import requests

vj = requests.get("https://piston-meta.mojang.com/v1/packages/0b21a8ab01286cddb2ef3af7b441bbced7bedf5e/1.21.4.json", timeout=60).json()
ai = requests.get(vj["assetIndex"]["url"], timeout=60).json()
objects = ai["objects"]

for term in ["barrier", "pumpkin", "fire"]:
    print(f"\n=== keys containing '{term}' ===")
    hits = [k for k in objects if term in k]
    for k in sorted(hits):
        print(f"  {k}")
