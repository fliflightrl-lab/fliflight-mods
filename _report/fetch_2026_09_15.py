#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fresh cross-platform stats fetch for Fliflightmc (15 Sep 2026)."""
import json, urllib.request, urllib.parse, datetime

CRED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json", encoding="utf-8"))
CF_KEY = CRED["curseforge"]["api_key"]
CF_AUTHOR = CRED["curseforge"]["author_id"]  # 123880127
MR_TOKEN = CRED["modrinth"]["token"]
MR_USER = CRED["modrinth"]["user_id"]        # sG9DNUJw

def get(url, headers=None, timeout=40):
    req = urllib.request.Request(url, headers=headers or {})
    req.add_header("User-Agent", "fliflight-report/1.0 (fliflight.rl@gmail.com)")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

out = {"fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}

# ---- CurseForge: enumerate ALL author mods via search pagination ----
cf_mods = {}
index = 0; page_size = 50
while True:
    url = (f"https://api.curseforge.com/v1/mods/search?gameId=432"
           f"&searchFilter={urllib.parse.quote('Fliflightmc')}&pageSize={page_size}&index={index}"
           f"&sortField=1&sortOrder=desc")
    d = get(url, {"x-api-key": CF_KEY})
    data = d.get("data", [])
    total = d.get("pagination", {}).get("totalCount", 0)
    for m in data:
        ids = {a.get("id") for a in m.get("authors", [])}
        if CF_AUTHOR in ids:
            cf_mods[m["id"]] = m
    index += page_size
    if index >= total or not data:
        break

# fetch full detail for downloadCount + dateReleased + categories
cf_rows = []
for mid, m in cf_mods.items():
    detail = get(f"https://api.curseforge.com/v1/mods/{mid}", {"x-api-key": CF_KEY})
    dd = detail.get("data", {})
    cf_rows.append({
        "id": mid,
        "name": m.get("name"),
        "slug": m.get("slug"),
        "classId": m.get("classId"),
        "downloads": dd.get("downloadCount", m.get("downloadCount", 0)),
        "dateReleased": dd.get("dateReleased"),
        "dateModified": dd.get("dateModified"),
        "categories": [c.get("name") for c in dd.get("categories", [])],
    })
out["curseforge"] = sorted(cf_rows, key=lambda r: -r["downloads"])

# ---- Modrinth: all projects ----
mr = get(f"https://api.modrinth.com/v2/user/{MR_USER}/projects", {"Authorization": MR_TOKEN})
out["modrinth"] = [{
    "id": p.get("id"), "slug": p.get("slug"), "title": p.get("title"),
    "project_type": p.get("project_type"), "downloads": p.get("downloads", 0),
    "followers": p.get("followers", 0), "status": p.get("status"),
    "published": p.get("published"), "updated": p.get("updated"),
} for p in mr]
out["modrinth"] = sorted(out["modrinth"], key=lambda r: -r["downloads"])

# ---- Modrinth user (monetization status) ----
mu = get(f"https://api.modrinth.com/v2/user/{MR_USER}", {"Authorization": MR_TOKEN})
out["modrinth_user"] = {"id": mu.get("id"), "username": mu.get("username"),
                        "payout_data": mu.get("payout_data"),
                        "role": mu.get("role"), "created": mu.get("created")}

# ---- GitHub ----
gh = {"repo": {}, "releases": [], "total_downloads": 0}
try:
    r = get("https://api.github.com/repos/fliflightrl-lab/fliflight-mods")
    gh["repo"] = {"stars": r.get("stargazers_count"), "forks": r.get("forks_count"),
                  "open_issues": r.get("open_issues_count"), "watchers": r.get("subscribers_count")}
    rels = get("https://api.github.com/repos/fliflightrl-lab/fliflight-mods/releases?per_page=100")
    for rel in rels:
        dl = sum(a.get("download_count", 0) for a in rel.get("assets", []))
        gh["releases"].append({"tag": rel.get("tag_name"), "downloads": dl,
                               "assets": len(rel.get("assets", [])),
                               "published": rel.get("published_at")})
    gh["total_downloads"] = sum(x["downloads"] for x in gh["releases"])
except Exception as e:
    gh["error"] = str(e)
out["github"] = gh

json.dump(out, open(r"C:\Users\user\fliflight-mods\_report\fresh_2026_09_15.json", "w", encoding="utf-8"),
          indent=2, ensure_ascii=False)
print(json.dumps(out, indent=2, ensure_ascii=False))
