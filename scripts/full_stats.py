#!/usr/bin/env python3
"""Full multi-platform stats: CurseForge + Modrinth downloads, deltas, percentages."""
import json, os, urllib.request, urllib.parse, sys

CREDS = os.path.expanduser("~/.config/fliflightmc/credentials.json")
STATE = os.path.expanduser("~/.config/fliflightmc/cf_downloads_baseline.json")

c = json.load(open(CREDS, encoding="utf-8"))
CF_KEY = c["curseforge"]["api_key"]
MR_TOKEN = c["modrinth"]["token"]
MR_USER = c["modrinth"]["user_id"]

def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    req.add_header("User-Agent", "fliflight-stats/1.0")
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)

def cf_mod(cid):
    return get(f"https://api.curseforge.com/v1/mods/{cid}", {"x-api-key": CF_KEY})["data"]

def mr_projects():
    return get(f"https://api.modrinth.com/v2/user/{MR_USER}/projects",
               {"Authorization": MR_TOKEN})

out = {}

# ---- CurseForge: known packs + any extra ----
CF_IDS = [
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
    (1653188, "PvP Essentials (flagship)"),
]

cf = {}
for cid, label in CF_IDS:
    try:
        d = cf_mod(cid)
        cf[cid] = {
            "label": label,
            "name": d.get("name", label),
            "downloads": d.get("downloadCount", 0),
            "classId": d.get("classId"),
            "slug": d.get("slug"),
            "url": f"https://www.curseforge.com/minecraft/{d.get('slug')}",
        }
    except Exception as e:
        cf[cid] = {"label": label, "downloads": None, "error": str(e)}

out["curseforge"] = cf

# ---- Modrinth ----
mr = {}
try:
    projs = mr_projects()
    for p in projs:
        mr[p["id"]] = {
            "slug": p.get("slug"),
            "title": p.get("title"),
            "downloads": p.get("downloads", 0),
            "followers": p.get("followers", 0),
            "project_type": p.get("project_type"),
            "url": f"https://modrinth.com/{p.get('project_type','project')}/{p.get('slug')}",
        }
except Exception as e:
    out["modrinth_error"] = str(e)

out["modrinth"] = mr

print(json.dumps(out, indent=2, ensure_ascii=False))
