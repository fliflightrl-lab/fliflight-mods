#!/usr/bin/env python3
"""For the two REJECTED projects: delete each gallery image and re-upload it with
a title + description (PATCH on old images is silently ignored while rejected)."""
import json, os, time
import requests

BASE = r"C:\Users\user\fliflight-mods"
PACKS = os.path.join(BASE, "packs")
CRED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))
HDR = {"Authorization": CRED["modrinth"]["token"], "User-Agent": "fliflightmc/1.0"}
API = "https://api.modrinth.com/v2"

JOBS = [
    ("fliflight-pvp-essentials", "cHpwGcrb", [
        ("01_crosshair.png",      "Dot crosshair", "The clean 1px dot crosshair - nothing blocking your view."),
        ("02_crosshair.png",      "Crosshair in action", "The dot crosshair during PvP combat."),
        ("03_visible_ores.png",   "Visible ores", "Every ore stands out so you never miss one."),
        ("04_visible_ores.png",   "Visible ores underground", "Spot ores instantly while mining."),
        ("05_visible_ores.png",   "Ores and ancient debris", "Ancient debris is visible too."),
        ("06_short_sword.png",    "Short sword", "Smaller, cleaner swords for better PvP visibility."),
        ("07_short_sword.png",    "Short sword in hand", "The sword no longer blocks your view."),
        ("08_clear_pumpkin.png",  "Clear pumpkin", "No more orange blur when wearing a pumpkin."),
        ("09_low_fire.png",       "Low fire", "The fire overlay sits lower, with the full flame animation."),
    ]),
    ("fliflight-clear-pumpkin", "xnQODGjN", [
        ("01_pumpkin.png", "Vanilla vs Clear Pumpkin", "Left: the orange pumpkin blur. Right: this pack - the blur is removed."),
        ("02_night.png",   "Wearing a pumpkin at night", "No orange veil, so mobs and terrain stay visible."),
    ]),
]

for slug, pid, items in JOBS:
    print("=" * 64)
    print(f"[{slug}]")
    # 1. wipe the gallery
    p = requests.get(f"{API}/project/{pid}", headers=HDR).json()
    for it in (p.get("gallery") or []):
        r = requests.delete(f"{API}/project/{pid}/gallery", headers=HDR, params={"url": it["url"]})
        print(f"    delete {it['url'][-22:]}: {r.status_code}")
        time.sleep(0.5)
    # 2. re-upload with titles
    for i, (fn, title, desc) in enumerate(items):
        path = os.path.join(PACKS, slug, "gallery", fn)
        if not os.path.exists(path):
            print(f"    !! missing {fn}")
            continue
        with open(path, "rb") as f:
            data = f.read()
        r = requests.post(f"{API}/project/{pid}/gallery",
                          headers={**HDR, "Content-Type": "image/png"},
                          params={"ext": "png", "featured": "true" if i == 0 else "false",
                                  "ordering": i, "title": title, "description": desc},
                          data=data)
        print(f"    [{i}] {title[:34]:<34} -> {r.status_code} {r.text[:60]}")
        time.sleep(1)

    # 3. verify
    p = requests.get(f"{API}/project/{pid}", headers=HDR).json()
    g = p.get("gallery") or []
    titled = sum(1 for x in g if x.get("title"))
    feat = sum(1 for x in g if x.get("featured"))
    print(f"    -> images={len(g)} titled={titled} featured={feat}")

print("\nDONE")
