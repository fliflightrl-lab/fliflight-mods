#!/usr/bin/env python3
"""Fetch the first 3 CurseForge screenshots + logo for each source pack of the flagship."""
import json, os
import requests

KEY = "$2a$10$0cAQe9NETJqOcxHCXkqww.MFCOHSEoZxGYL1xtkUbStvCQLAgcXIm"
HDR = {"x-api-key": KEY}
API = "https://api.curseforge.com/v1"

SOURCES = {
    "crosshair": 1499007,   # dot crosshair (#1)
    "ores":      1334611,   # visible ores
    "sword":     1334714,   # short sword
}

out_dir = r"C:\Users\user\fliflight-mods\packs\pvp-essentials\gallery_src"
os.makedirs(out_dir, exist_ok=True)

result = {}
for name, mid in SOURCES.items():
    r = requests.get(f"{API}/mods/{mid}", headers=HDR, timeout=30)
    r.raise_for_status()
    d = r.json()["data"]
    result[name] = {"name": d["name"], "slug": d["slug"],
                    "logo": d.get("logo", {}).get("url"),
                    "screenshots": []}
    ss = d.get("screenshots") or []
    print(f"\n=== {name} ({mid}) '{d['name']}' ===")
    print(f"  screenshots: {len(ss)}")
    for i, s in enumerate(ss[:3]):
        url = s.get("url")
        title = s.get("title") or "(no title)"
        print(f"  [{i}] {title}\n      {url}")
        result[name]["screenshots"].append({"title": title, "url": url})

with open(os.path.join(out_dir, "_source_images.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print("\nsaved ->", os.path.join(out_dir, "_source_images.json"))
