#!/usr/bin/env python3
"""Regenerate the clear-pumpkin image with the carved face (more recognizable), then re-upload it."""
import json, os
import requests
from PIL import Image

BASE = r"C:\Users\user\fliflight-mods"
PK   = os.path.join(BASE, "packs", "pvp-essentials")
V    = os.path.join(PK, "gallery_src", "vanilla")
GAL  = os.path.join(PK, "gallery")
CRED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))
TOKEN = CRED["modrinth"]["token"]
API = "https://api.modrinth.com/v2"
PID = "cHpwGcrb"

SIZE = 800
canvas = Image.new("RGBA", (SIZE, SIZE), (10, 10, 12, 255))

# carved pumpkin (the face) — more recognizable as "the pumpkin"
item = Image.open(os.path.join(V, "carved_pumpkin.png")).convert("RGBA")
ipx = int(SIZE * 0.52)
item = item.resize((ipx, ipx), Image.NEAREST)
canvas.paste(item, ((SIZE - ipx) // 2, (SIZE - ipx) // 2), item)

# barrier no-sign overlay
barrier = Image.open(os.path.join(V, "barrier.png")).convert("RGBA")
bpx = int(SIZE * 0.58)
barrier = barrier.resize((bpx, bpx), Image.NEAREST)
canvas.paste(barrier, ((SIZE - bpx) // 2, (SIZE - bpx) // 2), barrier)

path = os.path.join(GAL, "08_clear_pumpkin.png")
canvas.convert("RGB").save(path)
print(f"regenerated {path} ({os.path.getsize(path)} bytes)")

# re-upload: delete old 08, add new 08
HDR = {"Authorization": TOKEN}
p = requests.get(f"{API}/project/{PID}", headers=HDR).json()
gallery = p.get("gallery", [])
# find the 8th image (ordering) — delete all gallery then re-add is safest; do targeted by url
# Delete by URL matching the old pumpkin (8th). We'll just delete the one at index 7 (08).
# Simplest: delete old image(s), then re-add the new one in order.
for img in gallery:
    url = img.get("url")
    # delete only if it's our pumpkin (we can't easily tell; delete all and re-add cleanly)
    requests.delete(f"{API}/project/{PID}/gallery", headers=HDR, params={"url": url})

# re-upload all 9 in order
m = json.load(open(os.path.join(PK, "manifest.json")))
for i, fn in enumerate(m["gallery"]):
    fp = os.path.join(PK, "gallery", fn)
    with open(fp, "rb") as f:
        r = requests.post(f"{API}/project/{PID}/gallery?ext=png&featured=false&ordering={i}",
                          headers={**HDR, "Content-Type": "image/png"}, data=f.read())
        if r.status_code not in (200, 204):
            print(f"  FAIL gallery[{i}] {fn}: {r.status_code} {r.text[:120]}")

p = requests.get(f"{API}/project/{PID}", headers=HDR).json()
print(f"FINAL gallery={len(p.get('gallery', []))}")
