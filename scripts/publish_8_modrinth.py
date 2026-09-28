#!/usr/bin/env python3
"""Publish the 8 new packs on Modrinth: project -> icon -> gallery -> version -> review."""
import json, os, time
import requests

BASE = r"C:\Users\user\fliflight-mods"
PACKS = os.path.join(BASE, "packs")
CRED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))
HDR = {"Authorization": CRED["modrinth"]["token"]}
API = "https://api.modrinth.com/v2"

SLUGS = [
    "fliflight-low-shield",
    "fliflight-no-vignette",
    "fliflight-clear-water",
    "fliflight-clear-lava",
    "fliflight-clear-spyglass",
    "fliflight-clean-hotbar",
    "fliflight-thin-totem",
    "fliflight-clear-powder-snow",
]


def show(r, label):
    b = r.text.strip()
    print(f"    {label}: {r.status_code} {b[:110] if b else '(empty)'}")


valid = {gv["version"] for gv in requests.get(f"{API}/tag/game_version", headers=HDR).json()
         if gv.get("version_type") == "release"}

results = {}
for slug in SLUGS:
    print("=" * 62)
    print(f"[{slug}]")
    PK = os.path.join(PACKS, slug)
    m = json.load(open(os.path.join(PK, "manifest.json"), encoding="utf-8"))
    v = m["version"]
    gv = [x for x in v["game_versions"] if x in valid]
    print(f"    game versions kept: {len(gv)}/{len(v['game_versions'])}")

    if m.get("modrinth_id"):
        print(f"    already published: {m['modrinth_id']} — skipping")
        results[slug] = m["modrinth_id"]
        continue

    proj_data = {
        "slug": slug, "title": m["name"], "description": m["summary"],
        "categories": m["categories"], "game_versions": gv,
        "license_id": "LicenseRef-All-Rights-Reserved", "license_url": None,
        "project_type": "resourcepack",
        "client_side": "required", "server_side": "optional",
        "body": m["body"], "issues_url": None, "source_url": None,
        "wiki_url": None, "discord_url": None,
        "initial_versions": [], "is_draft": True,
        "disclosure_types": ["ai_content", "ai_content_assets"],
    }
    r = requests.post(f"{API}/project", headers=HDR,
                      files={"data": (None, json.dumps(proj_data), "application/json")})
    show(r, "create project")
    if r.status_code not in (200, 201):
        print("    FAILED:", r.text[:300]); continue
    pid = r.json()["id"]
    print(f"    project id: {pid}")

    with open(os.path.join(PK, "icon.png"), "rb") as f:
        show(requests.patch(f"{API}/project/{pid}/icon?ext=png",
                            headers={**HDR, "Content-Type": "image/png"}, data=f.read()), "icon")

    for i, fn in enumerate(m["gallery"]):
        with open(os.path.join(PK, "gallery", fn), "rb") as f:
            show(requests.post(
                f"{API}/project/{pid}/gallery",
                headers={**HDR, "Content-Type": "image/png"},
                params={"ext": "png", "featured": "true" if i == 0 else "false", "ordering": i,
                        "title": f"{m['name']} - before / after"},
                data=f.read()), f"gallery[{i}]")

    fname = m["file"]
    version_json = {
        "project_id": pid, "name": f"v{v['number']}", "version_number": v["number"],
        "changelog": v["changelog"], "dependencies": [], "game_versions": gv,
        "version_type": "release", "loaders": ["minecraft"], "featured": True,
        "file_parts": [fname], "primary_file": fname,
    }
    with open(os.path.join(PK, "files", fname), "rb") as f:
        show(requests.post(f"{API}/version", headers=HDR, files={
            "data": (None, json.dumps(version_json), "application/json"),
            fname: (fname, f, "application/zip")}), f"version {v['number']}")

    show(requests.patch(f"{API}/project/{pid}", headers=HDR, json={"status": "processing"}), "submit review")

    m["modrinth_id"] = pid
    with open(os.path.join(PK, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2, ensure_ascii=False)
    results[slug] = pid
    print(f"    URL: https://modrinth.com/resourcepack/{slug}")
    time.sleep(2)

print("\n" + "=" * 62)
print("SUMMARY")
for s, pid in results.items():
    print(f"  {s}: {pid}")
