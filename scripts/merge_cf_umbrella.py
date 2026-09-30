#!/usr/bin/env python3
"""Merge the 5 CurseForge-rejected micro-tweaks into ONE umbrella project,
each variation uploaded as a SEPARATE FILE (displayName = the tweak name).

This is the fix for the 'Merge Projects' rejection: one project, many files.

Usage:  python merge_cf_umbrella.py <UMBRELLA_PROJECT_ID>
"""
import json, os, sys
import requests

BASE = r"C:\Users\user\fliflight-mods"
CRED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))
TOKEN = CRED["curseforge"]["upload_token"]
VERSION_IDS = json.load(open(os.path.join(BASE, "dist", "cf_version_ids.json")))

# local folder -> short display name for the Files tab
VARIATIONS = [
    ("fliflight-clear-powder-snow", "Clear Powder Snow"),
    ("fliflight-thin-totem",        "Thin Totem"),
    ("fliflight-clean-hotbar",      "Clean Hotbar"),
    ("fliflight-clear-spyglass",    "Clear Spyglass"),
    ("fliflight-clear-lava",        "Clear Lava"),
]

def upload(project_id, folder, display_name):
    mf = os.path.join(BASE, "packs", folder, "manifest.json")
    m = json.load(open(mf, encoding="utf-8"))
    zip_path = os.path.join(BASE, "packs", folder, "files", m["file"])
    assert os.path.exists(zip_path), f"missing {zip_path}"

    # map version strings -> CF gameVersionIds (ints)
    ids, missing = [], []
    for v in m["version"]["game_versions"]:
        if v in VERSION_IDS:
            ids.append(int(VERSION_IDS[v]))
        else:
            missing.append(v)
    if missing:
        print(f"  !! {folder}: no CF id for {missing}")

    metadata = {
        "changelog": m["version"]["changelog"],
        "changelogType": "text",
        "displayName": display_name,
        "releaseType": "release",
        "gameVersions": ids,
    }
    url = f"https://minecraft.curseforge.com/api/projects/{project_id}/upload-file"
    with open(zip_path, "rb") as f:
        r = requests.post(
            url,
            headers={"X-Api-Token": TOKEN, "User-Agent": "fliflightmc/1.0"},
            files={"metadata": (None, json.dumps(metadata), "application/json"),
                   "file": (os.path.basename(zip_path), f, "application/zip")},
            timeout=120,
        )
    print(f"  {folder:<30} -> {r.status_code} {r.text[:120]}")
    return r.status_code == 200

if __name__ == "__main__":
    pid = sys.argv[1] if len(sys.argv) > 1 else None
    if not pid:
        print("usage: python merge_cf_umbrella.py <UMBRELLA_PROJECT_ID>")
        sys.exit(1)
    print(f"Uploading {len(VARIATIONS)} variations -> project {pid}")
    ok = 0
    for folder, name in VARIATIONS:
        try:
            ok += upload(pid, folder, name)
        except Exception as e:
            print(f"  {folder}: ERROR {e}")
    print(f"\n{ok}/{len(VARIATIONS)} uploaded")
