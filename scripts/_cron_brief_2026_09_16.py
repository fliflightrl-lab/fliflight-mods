#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Brief complet & fiable : téléchargements + revenus toutes plateformes (Fliflightmc)."""
import json, os, urllib.request, urllib.parse

HOME = os.path.expanduser("~")
CRED = json.load(open(os.path.join(HOME, ".config", "fliflightmc", "credentials.json"), encoding="utf-8"))
CF_KEY = CRED["curseforge"]["api_key"]
CF_AUTHOR = CRED["curseforge"]["author_id"]          # 123880127
MR_TOKEN = CRED["modrinth"]["token"]
MR_USER = CRED["modrinth"]["user_id"]                # sG9DNUJw
GH_REPO = "fliflightrl-lab/fliflight-mods"
SNAP = os.path.join(HOME, ".config", "fliflightmc", "platform_snapshot_2026-09-15.json")


def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    req.add_header("User-Agent", "fliflight-brief/1.0")
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))


# ---------- CurseForge (read API) ----------
cf_headers = {"x-api-key": CF_KEY}
cf_mods = []
index = 0
while True:
    u = (f"https://api.curseforge.com/v1/mods/search?gameId=432"
         f"&searchFilter={urllib.parse.quote('Fliflightmc')}&pageSize=50&index={index}")
    d = get(u, cf_headers)
    data = d.get("data", [])
    total = d.get("pagination", {}).get("totalCount", 0)
    for m in data:
        if any(a.get("id") == CF_AUTHOR for a in m.get("authors", [])):
            cf_mods.append(m)
    index += 50
    if index >= total or not data:
        break

# enrich downloadCount via mod detail (search often returns stale/0)
cf_rows = []
for m in cf_mods:
    mid = m.get("id")
    try:
        det = get(f"https://api.curseforge.com/v1/mods/{mid}", cf_headers)["data"]
        dl = det.get("downloadCount", 0)
    except Exception:
        dl = m.get("downloadCount", 0)
    cf_rows.append({
        "id": mid, "name": m.get("name"), "slug": m.get("slug"),
        "classId": m.get("classId"), "downloads": dl,
        "url": f"https://www.curseforge.com/minecraft/{m.get('slug')}",
    })

# ---------- Modrinth ----------
mr_projects = get(f"https://api.modrinth.com/v2/user/{MR_USER}/projects",
                  {"Authorization": MR_TOKEN})
mr_rows = [{
    "id": p.get("id"), "title": p.get("title"), "slug": p.get("slug"),
    "project_type": p.get("project_type"), "downloads": p.get("downloads", 0),
    "followers": p.get("followers", 0), "status": p.get("status"),
    "url": f"https://modrinth.com/{p.get('project_type','project')}/{p.get('slug')}",
} for p in mr_projects]

# ---------- GitHub Releases ----------
try:
    rels = get(f"https://api.github.com/repos/{GH_REPO}/releases?per_page=100")
    gh_total = sum(a.get("download_count", 0) for r in rels for a in r.get("assets", []))
    gh_err = None
except Exception as e:
    gh_total = None
    gh_err = str(e)

# ---------- compute ----------
cf_total = sum(r["downloads"] for r in cf_rows)
mr_total = sum(r["downloads"] for r in mr_rows)
mr_followers = sum(r["followers"] for r in mr_rows)
gh = gh_total or 0

# deltas vs 2026-09-15 snapshot
snap = json.load(open(SNAP, encoding="utf-8")) if os.path.exists(SNAP) else {}
prev_cf = {m["id"]: m["dl"] for m in snap.get("curseforge", {}).get("mods", [])}
prev_cf_total = snap.get("curseforge", {}).get("total_downloads", cf_total)
prev_mr_total = snap.get("modrinth", {}).get("total_downloads", mr_total)
prev_gh = snap.get("github", {}).get("mod_downloads", 0) + snap.get("github", {}).get("shorts_video_downloads", 0)
prev_grand = snap.get("grand_total_mods", 0)

grand = cf_total + mr_total + gh
cf_delta = cf_total - prev_cf_total
mr_delta = mr_total - prev_mr_total
gh_delta = gh - prev_gh
grand_delta = grand - prev_grand

out = {
    "fetched": "2026-09-16",
    "curseforge": {"total": cf_total, "projects": len(cf_rows), "rows": cf_rows},
    "modrinth": {"total": mr_total, "followers": mr_followers, "projects": len(mr_rows), "rows": mr_rows},
    "github": {"total": gh, "error": gh_err},
    "totals": {
        "grand": grand, "cf_total": cf_total, "mr_total": mr_total, "gh_total": gh,
    },
    "deltas_vs_2026_09_15": {
        "cf": cf_delta, "mr": mr_delta, "gh": gh_delta, "grand": grand_delta,
    },
}
print(json.dumps(out, ensure_ascii=False, indent=2))
