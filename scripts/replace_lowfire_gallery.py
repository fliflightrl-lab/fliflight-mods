#!/usr/bin/env python3
"""Replace ONLY the 'low fire' gallery image on Modrinth (09_low_fire.png).

Deletes the existing low-fire image (the one derived from the old/cut fire) and
uploads the regenerated one at the SAME ordering position, leaving every other
gallery image untouched.
"""
import json, os
import requests

BASE = r"C:\Users\user\fliflight-mods"
PK   = os.path.join(BASE, "packs", "pvp-essentials")
CRED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))
TOKEN = CRED["modrinth"]["token"]
HDR   = {"Authorization": TOKEN}
API   = "https://api.modrinth.com/v2"
PID   = "cHpwGcrb"
TARGET = "09_low_fire.png"
ORDER = 8   # position in the gallery list

def show(r, label):
    b = r.text.strip()
    print(f"{label}: {r.status_code} {b[:160] if b else '(empty)'}")

# 1. find the current low-fire gallery image
r = requests.get(f"{API}/project/{PID}", headers=HDR); r.raise_for_status()
p = r.json()
gallery = p.get("gallery", [])
print(f"current gallery: {len(gallery)} images")
print(f"gallery[8] (low fire) current url: {gallery[ORDER].get('url') if len(gallery)>ORDER else 'N/A'}")

# 2. delete the old low-fire image (match by its url)
old_url = gallery[ORDER].get("url") if len(gallery) > ORDER else None
if old_url:
    r = requests.delete(f"{API}/project/{PID}/gallery", headers=HDR, params={"url": old_url})
    show(r, f"  delete old low-fire {old_url[:70]}")

# 3. upload the new low-fire image at the same ordering
fp = os.path.join(PK, "gallery", TARGET)
with open(fp, "rb") as f:
    r = requests.post(
        f"{API}/project/{PID}/gallery?ext=png&featured=false&ordering={ORDER}",
        headers={**HDR, "Content-Type": "image/png"}, data=f.read())
show(r, f"  upload new {TARGET} (ordering={ORDER})")

# 4. verify
r = requests.get(f"{API}/project/{PID}", headers=HDR); r.raise_for_status()
g = r.json().get("gallery", [])
print(f"\nFINAL: gallery={len(g)} images")
for i, img in enumerate(g):
    print(f"  [{i}] {img.get('url','?')[:70]}")
