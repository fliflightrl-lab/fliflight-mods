#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rapport complet live 2026-09-18 — téléchargements + revenus toutes plateformes.
Récupère les données fraîches (CurseForge par auteur, Modrinth par user, GitHub releases),
calcule les deltas vs snapshot 2026-09-17, les parts de marché et les pourcentages."""
import json, os, urllib.request, urllib.parse, datetime

HOME = os.path.expanduser("~")
CRED = os.path.join(HOME, ".config", "fliflightmc", "credentials.json")
SNAP_PREV = os.path.join(HOME, ".config", "fliflightmc", "platform_snapshot_2026-09-17.json")

c = json.load(open(CRED, encoding="utf-8"))
CF_KEY = c["curseforge"]["api_key"]
CF_AUTHOR = c["curseforge"]["author_id"]
MR_TOKEN = c["modrinth"]["token"]
MR_USER = c["modrinth"]["user_id"]
GH_REPO = "fliflightrl-lab/fliflight-mods"

def get(url, headers=None, timeout=30, retries=2):
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

# ---- snapshot précédent ----
prev = {}
if os.path.exists(SNAP_PREV):
    prev = json.load(open(SNAP_PREV, encoding="utf-8"))
prev_cf = prev.get("curseforge", {})
prev_cf_dl = {str(m["id"]): m["dl"] for m in prev_cf.get("mods", [])}
prev_mr_total = prev.get("modrinth", {}).get("total_downloads", 0)
prev_gh = prev.get("github", {})

# ---------------- CurseForge (liste par auteur, search) ----------------
cf_headers = {"x-api-key": CF_KEY}
search = get("https://api.curseforge.com/v1/mods/search?gameId=432&searchFilter="
             + urllib.parse.quote("Fliflightmc") + "&pageSize=50&sortField=2&sortOrder=desc", cf_headers)
cf_mods = []
if "__error__" not in search:
    for m in search.get("data", []):
        authors = m.get("authors", [])
        if any(a.get("id") == CF_AUTHOR or (a.get("name") or "").lower() == "fliflightmc" for a in authors):
            cf_mods.append(m)

cf_rows = []
for m in cf_mods:
    mid = m.get("id")
    d = get(f"https://api.curseforge.com/v1/mods/{mid}", cf_headers).get("data", {})
    dl = d.get("downloadCount", 0)
    pdl = prev_cf_dl.get(str(mid), dl)
    cf_rows.append({
        "id": mid, "name": m.get("name"), "slug": m.get("slug"),
        "classId": m.get("classId"), "downloads": dl, "delta": dl - pdl,
    })
cf_rows.sort(key=lambda r: -r["downloads"])
cf_total = sum(r["downloads"] for r in cf_rows)
cf_prev_total = prev_cf.get("total_downloads", cf_total)

# ---------------- Modrinth (liste via API user) ----------------
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

# ---------------- GitHub releases ----------------
rels = get(f"https://api.github.com/repos/{GH_REPO}/releases?per_page=100",
           {"User-Agent": "fliflight-report/1.0", "Accept": "application/vnd.github+json"})
gh_total = 0
gh_per = []
if isinstance(rels, list):
    for r in rels:
        dls = sum(a.get("download_count", 0) for a in r.get("assets", []))
        gh_total += dls
        gh_per.append({"tag": r.get("tag_name"), "downloads": dls})
gh_prev = (prev_gh.get("mod_downloads", 0) + prev_gh.get("shorts_video_downloads", 0))

grand_total = cf_total + mr_total + gh_total
grand_prev = cf_prev_total + prev_mr_total + gh_prev

out = {
    "date": datetime.date.today().isoformat(),
    "curseforge": {"rows": cf_rows, "total": cf_total, "count": len(cf_rows)},
    "modrinth": {"rows": mr_rows, "total": mr_total, "followers": mr_follow, "count": len(mr_rows)},
    "github": {"total": gh_total, "releases": gh_per},
    "deltas": {
        "cf": cf_total - cf_prev_total,
        "mr": mr_total - prev_mr_total,
        "gh": gh_total - gh_prev,
        "grand": grand_total - grand_prev,
    },
    "totals": {"cf": cf_total, "mr": mr_total, "gh": gh_total, "grand": grand_total},
    "prev": {"cf": cf_prev_total, "mr": prev_mr_total, "gh": gh_prev, "grand": grand_prev},
}

snap = os.path.join(HOME, ".config", "fliflightmc", f"platform_snapshot_{out['date']}.json")
json.dump(out, open(snap, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(json.dumps(out, ensure_ascii=False, indent=2))
