#!/usr/bin/env python3
"""Publish the flagship 'PvP Essentials' resource pack to Modrinth (create project + version)."""
import json, os, sys
import requests

BASE = r"C:\Users\user\fliflight-mods"
PK   = os.path.join(BASE, "packs", "pvp-essentials")
CRED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))
TOKEN = CRED["modrinth"]["token"]
HDR   = {"Authorization": TOKEN}
API   = "https://api.modrinth.com/v2"

m = json.load(open(os.path.join(PK, "manifest.json")))
v = m["version"]
zip_path = os.path.join(PK, "files", m["file"])
fname = os.path.basename(zip_path)

def req(method, url, **kw):
    r = requests.request(method, url, headers=HDR, **kw)
    return r

# ---- validate game_versions against Modrinth's release list
r = req("GET", f"{API}/tag/game_version")
r.raise_for_status()
valid = {gv["version"] for gv in r.json() if gv.get("version_type") == "release"}
gv = [x for x in v["game_versions"] if x in valid]
missing = [x for x in v["game_versions"] if x not in valid]
if missing:
    print(f"NOTE: dropped non-release versions {missing}")
print(f"game_versions ({len(gv)}): {gv}")

# ---- 1. create project (two-step: draft project first)
project_json = {
    "slug": m["slug"],
    "title": m["name"],
    "description": m["summary"],
    "body": m["body"],
    "categories": m["categories"],
    "client_side": "required",
    "server_side": "optional",
    "project_type": "resourcepack",
    "license_id": "LicenseRef-All-Rights-Reserved",
    "initial_versions": [],
    "is_draft": True,
}
r = req("POST", f"{API}/project",
        files={"data": (None, json.dumps(project_json), "application/json")})
if r.status_code not in (200, 201):
    print("CREATE PROJECT FAILED", r.status_code, r.text)
    sys.exit(1)
pid = r.json()["id"]
print(f"project created: id={pid} status={r.json().get('status')}")

# ---- 2. create version with file
version_json = {
    "project_id": pid,
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
    r = req("POST", f"{API}/version", files=files)
if r.status_code not in (200, 201):
    print("CREATE VERSION FAILED", r.status_code, r.text)
    sys.exit(1)
vid = r.json()["id"]
print(f"version created: id={vid}")

# ---- 3. submit for review
r = req("PATCH", f"{API}/project/{pid}", json={"status": "processing"})
print(f"submit review: {r.status_code} status={r.json().get('status') if r.ok else r.text}")

# ---- 4. icon
icon_path = os.path.join(PK, m["icon"])
with open(icon_path, "rb") as f:
    r = req("PATCH", f"{API}/project/{pid}/icon?ext=png",
            data=f.read(), headers={**HDR, "Content-Type": "image/png"})
print(f"icon: {r.status_code}")

# ---- 5. gallery
gallery_path = os.path.join(PK, "gallery", m["gallery"][0])
with open(gallery_path, "rb") as f:
    r = req("POST", f"{API}/project/{pid}/gallery?ext=png&featured=false&ordering=0",
            data=f.read(), headers={**HDR, "Content-Type": "image/png"})
print(f"gallery: {r.status_code}")

print(f"\nDONE. Modrinth project id = {pid}  ->  https://modrinth.com/resourcepack/{m['slug']}")
