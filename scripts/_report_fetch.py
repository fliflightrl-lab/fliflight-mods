#!/usr/bin/env python3
import json, urllib.request, os

CREDS = os.path.expanduser("~/.config/fliflightmc/credentials.json")
creds = json.load(open(CREDS, encoding="utf-8"))
cf_key = creds["curseforge"]["api_key"]
mr_token = creds["modrinth"]["token"]
mr_uid = creds["modrinth"]["user_id"]

PACKS = [
    (1499007, "Dot Crosshair"),
    (1499029, "CrossX Crosshair"),
    (1494020, "Better Crosshair"),
    (1499072, "Bigger Dot"),
    (1497428, "CrosshairX"),
    (1588694, "Sniper Crosshair"),
    (1558798, "Crossy Crosshair"),
    (1334611, "Visible Ores"),
    (1334714, "Short Sword"),
    (1479652, "Diamond Dimension"),
]

def get(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)

cf_data = []
for cid, label in PACKS:
    try:
        d = get(f"https://api.curseforge.com/v1/mods/{cid}", {"x-api-key": cf_key})["data"]
        cf_data.append({
            "id": cid, "label": label, "name": d.get("name"),
            "downloads": d.get("downloadCount", 0),
            "classId": d.get("classId"),
            "summary": (d.get("summary") or "")[:80],
        })
    except Exception as e:
        cf_data.append({"id": cid, "label": label, "error": str(e)})

mr_data = []
try:
    projs = get(f"https://api.modrinth.com/v2/user/{mr_uid}/projects",
                {"Authorization": mr_token})
    for p in projs:
        mr_data.append({
            "id": p.get("id"), "slug": p.get("slug"),
            "title": p.get("title"), "status": p.get("status"),
            "project_type": p.get("project_type"),
            "downloads": p.get("downloads", 0),
            "followers": p.get("followers", 0),
        })
except Exception as e:
    mr_data = [{"error": str(e)}]

out = {"curseforge": cf_data, "modrinth": mr_data}
print(json.dumps(out, ensure_ascii=False, indent=2))
