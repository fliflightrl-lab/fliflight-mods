#!/usr/bin/env python3
"""Update Modrinth: body + upload the 9-image gallery in order (cleanup leftovers first)."""
import json, os
import requests

BASE = r"C:\Users\user\fliflight-mods"
PK   = os.path.join(BASE, "packs", "pvp-essentials")
CRED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))
TOKEN = CRED["modrinth"]["token"]
HDR   = {"Authorization": TOKEN}
API   = "https://api.modrinth.com/v2"
PID   = "cHpwGcrb"
m = json.load(open(os.path.join(PK, "manifest.json")))

def show(r, label):
    b = r.text.strip()
    print(f"{label}: {r.status_code} {b[:160] if b else '(empty)'}")

# 1. current state
r = requests.get(f"{API}/project/{PID}", headers=HDR)
r.raise_for_status()
p = r.json()
cur_gallery = p.get("gallery", [])
print(f"current gallery: {len(cur_gallery)} images")

# 2. delete leftover gallery images
for img in cur_gallery:
    url = img.get("url")
    if url:
        r = requests.delete(f"{API}/project/{PID}/gallery", headers=HDR, params={"url": url})
        show(r, f"  delete {url[:60]}")

# 3. update body
r = requests.patch(f"{API}/project/{PID}", headers=HDR, json={"body": m["body"]})
show(r, "update body")

# 4. upload gallery in order
gallery = m["gallery"]
for i, fn in enumerate(gallery):
    fp = os.path.join(PK, "gallery", fn)
    with open(fp, "rb") as f:
        r = requests.post(
            f"{API}/project/{PID}/gallery?ext=png&featured=false&ordering={i}",
            headers={**HDR, "Content-Type": "image/png"}, data=f.read())
    show(r, f"  gallery[{i}] {fn}")

# 5. final state
r = requests.get(f"{API}/project/{PID}", headers=HDR)
p = r.json()
print(f"\nFINAL: gallery={len(p.get('gallery', []))} images, status={p.get('status')}")
print(f"URL: https://modrinth.com/resourcepack/{p.get('slug')}")
