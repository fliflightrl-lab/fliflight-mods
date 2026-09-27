#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Brief live 2026-09-20 — téléchargements + revenus toutes plateformes."""
import json, os, urllib.request, urllib.parse, datetime

HOME = os.path.expanduser("~")
CRED = json.load(open(os.path.join(HOME, ".config", "fliflightmc", "credentials.json"), encoding="utf-8"))
CF_KEY = CRED["curseforge"]["api_key"]
CF_AUTHOR = CRED["curseforge"]["author_id"]
MR_TOKEN = CRED["modrinth"]["token"]
MR_USER = CRED["modrinth"]["user_id"]
GH_REPO = "fliflightrl-lab/fliflight-mods"
SNAP_PREV = os.path.join(HOME, ".config", "fliflightmc", "platform_snapshot_2026-09-18.json")

def get(url, headers=None, timeout=40, retries=2):
    last = None
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers or {})
            req.add_header("User-Agent", "fliflight-stats/1.0")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
    return {"__error__": str(last), "__url__": url}

prev = json.load(open(SNAP_PREV, encoding="utf-8")) if os.path.exists(SNAP_PREV) else {}
prev_cf_dl = {str(m["id"]): m["downloads"] for m in prev.get("curseforge", {}).get("rows", [])}
prev_cf_total = prev.get("totals", {}).get("cf", 0)
prev_mr_total = prev.get("totals", {}).get("mr", 0)
prev_gh_total = prev.get("totals", {}).get("gh", 0)
prev_grand = prev.get("totals", {}).get("grand", 0)

# ---------- CurseForge ----------
cf_headers = {"x-api-key": CF_KEY}
search = get("https://api.curseforge.com/v1/mods/search?gameId=432&searchFilter="
             + urllib.parse.quote("Fliflightmc") + "&pageSize=50&sortField=2&sortOrder=desc", cf_headers)
cf_rows = []
if "__error__" not in search:
    for m in search.get("data", []):
        authors = m.get("authors", [])
        if any(a.get("id") == CF_AUTHOR or (a.get("name") or "").lower() == "fliflightmc" for a in authors):
            mid = m.get("id")
            det = get(f"https://api.curseforge.com/v1/mods/{mid}", cf_headers).get("data", {})
            dl = det.get("downloadCount", m.get("downloadCount", 0))
            cf_rows.append({
                "id": mid, "name": m.get("name"), "slug": m.get("slug"),
                "classId": m.get("classId"), "downloads": dl,
                "delta": dl - prev_cf_dl.get(str(mid), dl),
            })
cf_rows.sort(key=lambda r: -r["downloads"])
cf_total = sum(r["downloads"] for r in cf_rows)

# ---------- Modrinth ----------
mr_headers = {"Authorization": MR_TOKEN}
projs = get(f"https://api.modrinth.com/v2/user/{MR_USER}/projects", mr_headers)
mr_rows = []
if isinstance(projs, list):
    for p in projs:
        mr_rows.append({
            "id": p.get("id"), "slug": p.get("slug"), "title": p.get("title"),
            "project_type": p.get("project_type"), "status": p.get("status"),
            "downloads": p.get("downloads", 0), "followers": p.get("followers", 0),
        })
mr_rows.sort(key=lambda r: -r["downloads"])
mr_total = sum(r["downloads"] for r in mr_rows)
mr_follow = sum(r["followers"] for r in mr_rows)

# Modrinth user (payout_data)
mr_user = get(f"https://api.modrinth.com/v2/user/{MR_USER}", mr_headers)

# ---------- GitHub ----------
rels = get(f"https://api.github.com/repos/{GH_REPO}/releases?per_page=100",
           {"Accept": "application/vnd.github+json"})
gh_total = 0
gh_per = []
if isinstance(rels, list):
    for r in rels:
        dls = sum(a.get("download_count", 0) for a in r.get("assets", []))
        gh_total += dls
        gh_per.append({"tag": r.get("tag_name"), "downloads": dls})
repo = get(f"https://api.github.com/repos/{GH_REPO}", {"Accept": "application/vnd.github+json"})
repo_meta = {"stars": repo.get("stargazers_count"), "forks": repo.get("forks_count")} if isinstance(repo, dict) else {}

grand_total = cf_total + mr_total + gh_total

out = {
    "date": datetime.date.today().isoformat(),
    "curseforge": {"rows": cf_rows, "total": cf_total, "count": len(cf_rows)},
    "modrinth": {"rows": mr_rows, "total": mr_total, "followers": mr_follow, "count": len(mr_rows)},
    "modrinth_user": mr_user,
    "github": {"total": gh_total, "releases": gh_per, "repo": repo_meta},
    "totals": {"cf": cf_total, "mr": mr_total, "gh": gh_total, "grand": grand_total},
    "prev": {"cf": prev_cf_total, "mr": prev_mr_total, "gh": prev_gh_total, "grand": prev_grand},
    "deltas": {
        "cf": cf_total - prev_cf_total,
        "mr": mr_total - prev_mr_total,
        "gh": gh_total - prev_gh_total,
        "grand": grand_total - prev_grand,
    },
}

snap = os.path.join(HOME, ".config", "fliflightmc", f"platform_snapshot_{out['date']}.json")
json.dump(out, open(snap, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(json.dumps(out, ensure_ascii=False, indent=2))
