#!/usr/bin/env python3
"""Upload the redesigned icons to Modrinth and rename 'No Vignette' -> 'No Dark Corners'
(jargon-free name; slug updated to match, as Modrinth asks)."""
import json, os
import requests

BASE = r"C:\Users\user\fliflight-mods"
CRED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))
HDR = {"Authorization": CRED["modrinth"]["token"], "User-Agent": "fliflightmc/1.0"}
API = "https://api.modrinth.com/v2"

ICONS = {
    "fliflight-low-shield":        "3kHplXd9",
    "fliflight-no-vignette":       "JYyEzln5",
    "fliflight-clear-water":       "4KyMcPC1",
    "fliflight-clear-lava":        "eG9N5405",
    "fliflight-clear-spyglass":    "HEAEl6k5",
    "fliflight-clean-hotbar":      "PDnvunp5",
    "fliflight-thin-totem":        "32hlofGi",
    "fliflight-clear-powder-snow": "fQlGVRS8",
    "fliflight-clear-pumpkin":     "xnQODGjN",
}

print("=== ICONS ===")
for slug, pid in ICONS.items():
    path = os.path.join(BASE, "dist", "cf_logos", slug + "-512.png")
    if not os.path.exists(path):
        print(f"  {slug}: MISSING {path}")
        continue
    with open(path, "rb") as f:
        data = f.read()
    r = requests.patch(f"{API}/project/{pid}/icon", headers={**HDR, "Content-Type": "image/png"},
                       params={"ext": "png"}, data=data)
    print(f"  {slug:<30} {len(data):>6} B -> {r.status_code} {r.text[:60]}")

print("\n=== RENAME: No Vignette -> No Dark Corners ===")
new_title = "No Dark Corners"
new_slug = "fliflight-no-dark-corners"
r = requests.patch(f"{API}/project/JYyEzln5", headers=HDR, json={"title": new_title})
print(f"  title -> {r.status_code} {r.text[:80]}")
r = requests.patch(f"{API}/project/JYyEzln5", headers=HDR, json={"slug": new_slug})
print(f"  slug  -> {r.status_code} {r.text[:80]}")

# verify + record in the manifest
p = requests.get(f"{API}/project/fliflight-no-dark-corners", headers=HDR).json()
print(f"  now: title={p['title']!r} slug={p['slug']!r} status={p['status']}")

mf = os.path.join(BASE, "packs", "fliflight-no-vignette", "manifest.json")
m = json.load(open(mf, encoding="utf-8"))
m["slug"] = "fliflight-no-dark-corners"
m["name"] = "No Dark Corners"
m["summary"] = "Removes the dark shading in the corners of the screen, so the whole view stays evenly lit."
m["body"] = m["body"].replace("**No Vignette - Brighter Screen, No Dark Corners**", "**No Dark Corners**")
json.dump(m, open(mf, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"  manifest updated ({mf})")
