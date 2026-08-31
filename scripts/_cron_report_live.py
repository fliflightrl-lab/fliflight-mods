#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rapport complet live: téléchargements + revenus sur CurseForge, Modrinth, GitHub.
Récupère les données fraîches (pas d'IDs Modrinth codés en dur -> liste via API user)."""
import json, os, urllib.request, urllib.parse, datetime

HOME = os.path.expanduser("~")
CRED = os.path.join(HOME, ".config", "fliflightmc", "credentials.json")
CF_BASE = os.path.join(HOME, ".config", "fliflightmc", "cf_downloads_baseline.json")
PREV_REPORT = os.path.join(HOME, ".config", "fliflightmc", "report_all_platforms.json")

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
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
    return {"__error__": str(last), "__url__": url}

out = {}
now = datetime.datetime.now().isoformat(timespec="seconds")

# ---------------- CurseForge (liste par auteur) ----------------
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
    cf_rows.append({
        "id": mid, "name": m.get("name"), "slug": m.get("slug"),
        "classId": m.get("classId"),
        "downloads": d.get("downloadCount", 0),
        "dateReleased": (d.get("dateReleased") or "")[:10],
        "dateModified": (d.get("dateModified") or "")[:10],
    })
cf_rows.sort(key=lambda r: -r["downloads"])
out["curseforge"] = {"rows": cf_rows, "total": sum(r["downloads"] for r in cf_rows), "count": len(cf_rows)}

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
            "published": (p.get("published") or "")[:10], "updated": (p.get("updated") or "")[:10],
        })
else:
    mr_rows = [{"__error__": projs.get("__error__")}]
mr_rows.sort(key=lambda r: -r.get("downloads", 0))
out["modrinth"] = {"rows": mr_rows, "total": sum(r.get("downloads", 0) for r in mr_rows),
                   "followers": sum(r.get("followers", 0) for r in mr_rows), "count": len(mr_rows)}

# ---------------- Modrinth monetisation (CMP / payouts) ----------------
for path in [f"/v2/user/{MR_USER}/payouts", "/v2/payouts", f"/v2/user/{MR_USER}/monetization",
             "/v2/organization/monetization", f"/v2/user/{MR_USER}"]:
    r = get("https://api.modrinth.com" + path, mr_headers)
    out["mr_"+path.strip("/").replace("/", "_")] = r

# ---------------- CurseForge rewards (auteurs) ----------------
# Rewards = dashboard auteurs, pas dans l'API publique. On tente néanmoins.
for path in ["https://authors.curseforge.com/api/rewards",
             "https://authors.curseforge.com/api/rewards/summary",
             "https://api.curseforge.com/v1/mods/rewards"]:
    r = get(path, cf_headers)
    out["cf_rewards_"+path.split("/")[-1]] = r

# ---------------- GitHub releases ----------------
try:
    rels = get(f"https://api.github.com/repos/{GH_REPO}/releases?per_page=100",
               {"User-Agent": "fliflight-report/1.0", "Accept": "application/vnd.github+json"})
except Exception as e:
    rels = {"__error__": str(e)}
gh_total = 0
gh_per = []
if isinstance(rels, list):
    for r in rels:
        dls = sum(a.get("download_count", 0) for a in r.get("assets", []))
        gh_total += dls
        gh_per.append({"tag": r.get("tag_name"), "downloads": dls})
out["github"] = {"total": gh_total, "releases": gh_per}
out["generated_at"] = now

# ---------------- Écrire le snapshot ----------------
snap = os.path.join(HOME, ".config", "fliflightmc", "report_snapshot.json")
json.dump(out, open(snap, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# Résumé court imprimé
print(json.dumps({
    "curseforge_total": out["curseforge"]["total"],
    "curseforge_count": out["curseforge"]["count"],
    "modrinth_total": out["modrinth"]["total"],
    "modrinth_count": out["modrinth"]["count"],
    "github_total": gh_total,
}, ensure_ascii=False, indent=2))
