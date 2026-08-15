#!/usr/bin/env python3
"""Read pack.mcmeta from existing packs to match pack_format."""
import zipfile, os, json

BASE = r"C:\Users\user\fliflight-mods\packs"
TARGETS = {
    "dot":   r"dot-crosshair-cossx-better-crosshair/files/best_crosshair-1.0.0-resourcepack-1.21.4.zip",
    "ores":  r"visible-ores-all-versions-and-netherite/files/visible_ores-1.0.0-resourcepack-.zip",
    "sword": r"pvp-sword-little-sword-all-versions/files/better_little_sword-1.0.0-resourcepack-1.21.4.zip",
}

for name, rel in TARGETS.items():
    p = os.path.join(BASE, rel)
    with zipfile.ZipFile(p) as z:
        raw = z.read("pack.mcmeta")
        print(f"=== {name} ===")
        print(raw.decode("utf-8").strip())
        print()
