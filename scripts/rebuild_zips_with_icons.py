#!/usr/bin/env python3
"""Rebuild the pack zips so the in-game icon (pack.png) matches the new store icons,
then refresh dist/TESTEZ-MOI/ and the test sheet."""
import os, shutil, zipfile

BASE = r"C:\Users\user\fliflight-mods"
PACKS = os.path.join(BASE, "packs")
BUILD = os.path.join(BASE, "build")
DIST = os.path.join(BASE, "dist")

# local folder -> (version zip suffix)
JOBS = [
    ("fliflight-low-shield", "fliflight-low-shield"),
    ("fliflight-no-vignette", "fliflight-no-dark-corners"),      # renamed on the store
    ("fliflight-clear-water", "fliflight-clear-water"),
    ("fliflight-clear-lava", "fliflight-clear-lava"),
    ("fliflight-clear-spyglass", "fliflight-clear-spyglass"),
    ("fliflight-clean-hotbar", "fliflight-clean-hotbar"),
    ("fliflight-thin-totem", "fliflight-thin-totem"),
    ("fliflight-clear-powder-snow", "fliflight-clear-powder-snow"),
    ("fliflight-clear-pumpkin", "fliflight-clear-pumpkin"),
]

VERSION = "1.0.0"
test_dir = os.path.join(DIST, "TESTEZ-MOI")
os.makedirs(test_dir, exist_ok=True)

for folder, zipbase in JOBS:
    stage = os.path.join(BUILD, folder)
    icon = os.path.join(PACKS, folder, "pack.png")
    if not os.path.isdir(stage):
        print(f"  !! no build stage for {folder}")
        continue
    if os.path.exists(icon):
        shutil.copy2(icon, os.path.join(stage, "pack.png"))
    zp = os.path.join(DIST, f"{zipbase}-{VERSION}-resourcepack-1.21.4.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(stage):
            for fn in files:
                full = os.path.join(root, fn)
                z.write(full, os.path.relpath(full, stage).replace("\\", "/"))
    # keep the pack's own files/ copy in sync
    os.makedirs(os.path.join(PACKS, folder, "files"), exist_ok=True)
    shutil.copy2(zp, os.path.join(PACKS, folder, "files", os.path.basename(zp)))
    shutil.copy2(zp, os.path.join(test_dir, os.path.basename(zp)))
    # verify the icon made it in
    with zipfile.ZipFile(zp) as z:
        has_icon = "pack.png" in z.namelist()
    print(f"  {zipbase}: {os.path.getsize(zp):>6} B  pack.png={'yes' if has_icon else 'MISSING'}")

print("\nTESTEZ-MOI:", len(os.listdir(test_dir)), "zips")
