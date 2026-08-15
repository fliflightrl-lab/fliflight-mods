#!/usr/bin/env python3
"""Create + publish the two standalone QoL packs on Modrinth:
  - fliflight-low-fire
  - fliflight-clear-pumpkin
Steps per pack: create project -> upload icon -> upload gallery -> create version.
"""
import json, os
import requests

BASE = r"C:\Users\user\fliflight-mods"
PACKS = os.path.join(BASE, "packs")
CRED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))
TOKEN = CRED["modrinth"]["token"]
HDR = {"Authorization": TOKEN}
API = "https://api.modrinth.com/v2"

def show(r, label):
    b = r.text.strip()
    print(f"{label}: {r.status_code} {b[:120] if b else '(empty)'}")

def publish(slug):
    PK = os.path.join(PACKS, slug)
    m = json.load(open(os.path.join(PK, "manifest.json")))
    v = m["version"]

    # valid game versions
    valid = {gv["version"] for gv in requests.get(f"{API}/tag/game_version", headers=HDR).json()
             if gv.get("version_type") == "release"}
    gv = [x for x in v["game_versions"] if x in valid]

    # 1. create project (Modrinth expects multipart with a "data" JSON field;
    #    draft first with empty initial_versions, same as the flagship script)
    proj_data = {
        "slug": slug, "title": m["name"], "description": m["summary"],
        "categories": m["categories"], "game_versions": gv,
        "license_id": "LicenseRef-All-Rights-Reserved", "license_url": None,
        "project_type": "resourcepack",
        "client_side": "required", "server_side": "optional",
        "body": m["body"], "issues_url": None, "source_url": None,
        "wiki_url": None, "discord_url": None,
        "initial_versions": [], "is_draft": True,
    }
    files = {"data": (None, json.dumps(proj_data), "application/json")}
    r = requests.post(f"{API}/project", headers=HDR, files=files)
    show(r, "create project")
    if r.status_code not in (200, 201):
        print(r.text); raise SystemExit(1)
    pid = r.json()["id"]
    print(f"  project id: {pid}")

    # 2. icon
    with open(os.path.join(PK, "icon.png"), "rb") as f:
        r = requests.patch(f"{API}/project/{pid}/icon?ext=png",
                           headers={**HDR, "Content-Type": "image/png"}, data=f.read())
    show(r, "icon")

    # 3. gallery
    for i, fn in enumerate(m["gallery"]):
        with open(os.path.join(PK, "gallery", fn), "rb") as f:
            r = requests.post(f"{API}/project/{pid}/gallery?ext=png&featured=false&ordering={i}",
                              headers={**HDR, "Content-Type": "image/png"}, data=f.read())
        show(r, f"gallery[{i}] {fn}")

    # 4. version
    fname = m["file"]
    zip_path = os.path.join(PK, "files", fname)
    version_json = {
        "project_id": pid, "name": f"v{v['number']}", "version_number": v["number"],
        "changelog": v["changelog"], "dependencies": [], "game_versions": gv,
        "version_type": "release", "loaders": ["minecraft"], "featured": True,
        "file_parts": [fname], "primary_file": fname,
    }
    with open(zip_path, "rb") as f:
        files = {"data": (None, json.dumps(version_json), "application/json"),
                 fname: (fname, f, "application/zip")}
        r = requests.post(f"{API}/version", headers=HDR, files=files)
    show(r, f"create version {v['number']}")

    # 5. submit for review
    r = requests.patch(f"{API}/project/{pid}", headers=HDR, json={"status": "processing"})
    show(r, "submit review")

    # 6. save the project id back into the manifest
    m["modrinth_id"] = pid
    with open(os.path.join(PK, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2)
    print(f"  URL: https://modrinth.com/resourcepack/{slug}\n")
    return pid

for slug in ["fliflight-low-fire", "fliflight-clear-pumpkin"]:
    print("=" * 60)
    publish(slug)
print("DONE")
