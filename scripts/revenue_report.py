#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rassemble téléchargements + revenus sur CurseForge & Modrinth pour Fliflightmc."""
import json, sys, urllib.request, urllib.parse

CRED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json", encoding="utf-8"))
CF_KEY = CRED["curseforge"]["api_key"]
CF_AUTHOR = CRED["curseforge"]["author_id"]
MR_TOKEN = CRED["modrinth"]["token"]
MR_USER = CRED["modrinth"]["user_id"]

def get(url, headers=None, retries=2):
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == retries:
                return {"__error__": str(e), "__url__": url}

out = {}

# ---- CurseForge ----
cf_headers = {"x-api-key": CF_KEY}
search = get(f"https://api.curseforge.com/v1/mods/search?gameId=432&searchFilter={urllib.parse.quote('Fliflightmc')}&pageSize=50&sortField=2&sortOrder=desc", cf_headers)
cf_mods = []
if "__error__" not in search:
    for m in search.get("data", []):
        authors = m.get("authors", [])
        if any(a.get("id") == CF_AUTHOR or a.get("name", "").lower() == "fliflightmc" for a in authors):
            cf_mods.append(m)
out["curseforge"] = {"total": len(cf_mods), "mods": []}
for m in cf_mods:
    mid = m.get("id")
    detail = get(f"https://api.curseforge.com/v1/mods/{mid}", cf_headers)
    d = detail.get("data", {})
    out["curseforge"]["mods"].append({
        "id": mid,
        "name": m.get("name"),
        "slug": m.get("slug"),
        "classId": m.get("classId"),
        "downloadCount": d.get("downloadCount"),
        "summary": d.get("summary"),
        "releaseDate": (d.get("dateReleased") or ""),
        "lastUpdated": (d.get("dateModified") or ""),
    })

# ---- Modrinth ----
mr_headers = {"Authorization": MR_TOKEN}
projs = get(f"https://api.modrinth.com/v2/user/{MR_USER}/projects", mr_headers)
out["modrinth"] = {"projects": []}
if "__error__" not in projs:
    for p in projs:
        out["modrinth"]["projects"].append({
            "id": p.get("id"),
            "slug": p.get("slug"),
            "title": p.get("title"),
            "project_type": p.get("project_type"),
            "downloads": p.get("downloads"),
            "followers": p.get("followers"),
            "status": p.get("status"),
            "published": p.get("published"),
            "updated": p.get("updated"),
        })

# ---- Revenus / payout data ----
mr_user = get(f"https://api.modrinth.com/v2/user/{MR_USER}", mr_headers)
out["modrinth_user"] = mr_user if isinstance(mr_user, dict) else {}

# Essayer les endpoints de payout Modrinth (CMP)
for path in ["/v2/user/%s/payouts" % MR_USER, "/v2/payouts"]:
    r = get(f"https://api.modrinth.com{path}", mr_headers)
    out["mr_payout_%s" % path.replace("/", "_")] = r

# CurseForge rewards (essai de quelques endpoints connus)
for path in [
    "https://authors.curseforge.com/api/rewards",
    "https://api.curseforge.com/v1/mods/1653188",
]:
    pass  # déjà couvert

print(json.dumps(out, ensure_ascii=False, indent=2))
