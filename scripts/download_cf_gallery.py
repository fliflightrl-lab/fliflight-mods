#!/usr/bin/env python3
"""Download the CurseForge screenshots into the flagship gallery staging."""
import json, os
import requests

out_dir = r"C:\Users\user\fliflight-mods\packs\pvp-essentials\gallery_src"
src = json.load(open(os.path.join(out_dir, "_source_images.json"), encoding="utf-8"))

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
downloaded = []
for name, info in src.items():
    for i, s in enumerate(info["screenshots"]):
        url = s["url"]
        ext = ".png" if url.lower().endswith(".png") else ".jpg"
        fn = f"{name}_{i}{ext}"
        r = requests.get(url, headers=UA, timeout=60)
        r.raise_for_status()
        path = os.path.join(out_dir, fn)
        with open(path, "wb") as f:
            f.write(r.content)
        downloaded.append((fn, len(r.content)))
        print(f"  {fn:28s} {len(r.content):>9} bytes")

print(f"\n{len(downloaded)} images downloaded.")
