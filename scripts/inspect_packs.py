#!/usr/bin/env python3
"""Extract and inspect the winning packs' real contents."""
import zipfile, os, sys

BASE = r"C:\Users\user\fliflight-mods\packs"
TARGETS = {
    "dot":       r"dot-crosshair-cossx-better-crosshair/files/best_crosshair-1.0.0-resourcepack-1.21.4.zip",
    "ores":      r"visible-ores-all-versions-and-netherite/files/visible_ores-1.0.0-resourcepack-.zip",
    "sword":     r"pvp-sword-little-sword-all-versions/files/better_little_sword-1.0.0-resourcepack-1.21.4.zip",
}

for name, rel in TARGETS.items():
    p = os.path.join(BASE, rel)
    print(f"\n=== {name} ===")
    if not os.path.exists(p):
        print("  NOT FOUND:", p)
        # list actual files
        d = os.path.dirname(p)
        if os.path.isdir(d):
            print("  actual files:", os.listdir(d))
        continue
    with zipfile.ZipFile(p) as z:
        for i in z.infolist():
            print(f"  {i.filename:60s} {i.file_size:>8}")
