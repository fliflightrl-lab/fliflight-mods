#!/usr/bin/env python3
"""Publish the manifest's current version to Modrinth; keep only the latest version."""
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
v = m["version"]
fname = m["file"]
zip_path = os.path.join(PK, "files", fname)

valid = {gv["version"] for gv in requests.get(f"{API}/tag/game_version", headers=HDR).json()
         if gv.get("version_type") == "release"}
gv = [x for x in v["game_versions"] if x in valid]

version_json = {
    "project_id": PID, "name": f"v{v['number']}", "version_number": v["number"],
    "changelog": v["changelog"], "dependencies": [], "game_versions": gv,
    "version_type": "release", "loaders": ["minecraft"], "featured": True,
    "file_parts": [fname], "primary_file": fname,
}
with open(zip_path, "rb") as f:
    files = {"data": (None, json.dumps(version_json), "application/json"),
             fname: (fname, f, "application/zip")}
    r = requests.post(f"{API}/version", headers=HDR, files=files)
print(f"create {v['number']}: {r.status_code}")
new_id = r.json()["id"] if r.status_code in (200, 201) else None

# delete older versions (keep only latest)
p = requests.get(f"{API}/project/{PID}", headers=HDR).json()
for vid in p.get("versions", []):
    if vid != new_id:
        rd = requests.delete(f"{API}/version/{vid}", headers=HDR)
        print(f"delete old version {vid}: {rd.status_code}")

p = requests.get(f"{API}/project/{PID}", headers=HDR).json()
print(f"project versions now: {len(p.get('versions', []))}")
for vid in p.get("versions", []):
    vv = requests.get(f"{API}/version/{vid}", headers=HDR).json()
    print(f"  v{vv.get('version_number')}")
