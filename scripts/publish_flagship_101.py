#!/usr/bin/env python3
"""Create Modrinth version 1.0.1 (fixed fire) on the existing flagship project."""
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

# validate game_versions
valid = {gv["version"] for gv in requests.get(f"{API}/tag/game_version", headers=HDR).json()
         if gv.get("version_type") == "release"}
gv = [x for x in v["game_versions"] if x in valid]
print(f"game_versions: {len(gv)}")

version_json = {
    "project_id": PID,
    "name": f"v{v['number']}",
    "version_number": v["number"],
    "changelog": v["changelog"],
    "dependencies": [],
    "game_versions": gv,
    "version_type": "release",
    "loaders": ["minecraft"],
    "featured": True,
    "file_parts": [fname],
    "primary_file": fname,
}
with open(zip_path, "rb") as f:
    files = {
        "data": (None, json.dumps(version_json), "application/json"),
        fname: (fname, f, "application/zip"),
    }
    r = requests.post(f"{API}/version", headers=HDR, files=files)
print(f"create version: {r.status_code} {r.text[:300] if r.status_code not in (200,201) else ''}")
if r.status_code in (200, 201):
    print(f"version id={r.json()['id']}")

# verify
p = requests.get(f"{API}/project/{PID}", headers=HDR).json()
print(f"project versions: {len(p.get('versions', []))}, status={p.get('status')}")
for vid in p.get("versions", []):
    vv = requests.get(f"{API}/version/{vid}", headers=HDR).json()
    print(f"  v{vv.get('version_number')}  files={[f['filename'] for f in vv.get('files', [])]}")
