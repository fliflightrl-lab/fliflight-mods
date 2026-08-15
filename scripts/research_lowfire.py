#!/usr/bin/env python3
"""Research: download a popular 'low fire' resource pack from Modrinth and inspect its fire textures."""
import json, os, io, zipfile
import requests
from PIL import Image

HDR = {"Authorization": json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))["modrinth"]["token"]}
API = "https://api.modrinth.com/v2"

# search low fire resource packs
r = requests.get(f"{API}/search", headers=HDR, params={
    "query": "low fire", "limit": 10,
    "facets": json.dumps([["project_type:resourcepack"]]),
})
r.raise_for_status()
hits = r.json()["hits"]
print("Top low-fire packs:")
for h in hits[:5]:
    print(f"  {h['slug']:40s} downloads={h['downloads']:>8}")

if not hits:
    print("no hits"); raise SystemExit

# pick the most-downloaded
best = max(hits, key=lambda h: h["downloads"])
slug = best["slug"]
print(f"\nInspecting: {slug} ({best['downloads']} downloads)")

# get versions + first file
ver = requests.get(f"{API}/project/{slug}/version", headers=HDR).json()
vf = None
for v in ver:
    if v.get("files"):
        vf = v
        break
if not vf:
    print("no files"); raise SystemExit

furl = vf["files"][0]["url"]
fname = vf["files"][0]["filename"]
print(f"downloading {fname} ...")
data = requests.get(furl).content
with zipfile.ZipFile(io.BytesIO(data)) as z:
    fire_files = [n for n in z.namelist() if "fire" in n.lower() and n.endswith(".png")]
    print(f"fire-related files in this pack: {fire_files}")
    for fn in fire_files:
        img = Image.open(io.BytesIO(z.read(fn))).convert("RGBA")
        px = img.load()
        w, h = img.size
        # opaque pixel distribution (top vs bottom half of first frame)
        fh = min(w, h)  # frame height (assume square frame)
        top = sum(1 for y in range(fh//2) for x in range(w) if px[x, y][3] > 30)
        bot = sum(1 for y in range(fh//2, fh) for x in range(w) if px[x, y][3] > 30)
        print(f"  {fn}: {img.size}  frame0 top={top} bottom={bot}")
