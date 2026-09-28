import json, urllib.request, urllib.parse, datetime, time

CF_KEY = "$2a$10$Uvg9i4yTuWKGujo0hQbVaOvOb9i1b2QqikOmDB2pEk2hACZE5n08O"
MR_TOKEN = "mrp_BuW9lcEew20QyOIPdCxYhx6APN5bCh0usOZbSycTsNHlmm2jhiFOrR3GOeLI"
MR_USER = "sG9DNUJw"
CF_AUTHOR = "Fliflightmc"

def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    req.add_header("User-Agent", "fliflight-report/1.0")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

out = {"fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}

# ---- CurseForge author mods ----
cf_mods = []
index = 0; page_size = 50
while True:
    url = (f"https://api.curseforge.com/v1/mods/search?gameId=432"
           f"&searchFilter={urllib.parse.quote(CF_AUTHOR)}&pageSize={page_size}&index={index}")
    d = get(url, {"x-api-key": CF_KEY})
    data = d.get("data", [])
    total = d.get("pagination", {}).get("totalCount", 0)
    for m in data:
        names = [a.get("name","") for a in m.get("authors",[])]
        if CF_AUTHOR in names:
            cf_mods.append({
                "id": m.get("id"), "name": m.get("name"),
                "downloadCount": m.get("downloadCount", 0),
                "slug": m.get("slug"), "classId": m.get("classId"),
            })
    index += page_size
    if index >= total or not data:
        break
out["curseforge"] = cf_mods

# ---- Modrinth projects ----
mr = get(f"https://api.modrinth.com/v2/user/{MR_USER}/projects", {"Authorization": MR_TOKEN})
out["modrinth"] = [{"id": p.get("id"), "title": p.get("title"), "slug": p.get("slug"),
                    "project_type": p.get("project_type"), "downloads": p.get("downloads", 0),
                    "followers": p.get("followers", 0)} for p in mr]

# ---- GitHub ----
out["github"] = {}
try:
    gh = get("https://api.github.com/repos/fliflightrl-lab/fliflight-mods")
    out["github"]["repo"] = {"stargazers": gh.get("stargazers_count"), "forks": gh.get("forks_count"),
                             "open_issues": gh.get("open_issues_count")}
    rels = get("https://api.github.com/repos/fliflightrl-lab/fliflight-mods/releases?per_page=100")
    gh_releases = []
    for r in rels:
        dl = sum(a.get("download_count", 0) for a in r.get("assets", []))
        gh_releases.append({"tag": r.get("tag_name"), "downloads": dl, "assets": len(r.get("assets", []))})
    out["github"]["releases"] = gh_releases
except Exception as e:
    out["github"]["error"] = str(e)

# ---- Revenue probe endpoints (CurseForge Rewards / Modrinth payouts) ----
out["revenue_probe"] = {}
cf_rp = [
    "https://api.curseforge.com/v1/mods/rewards",
    "https://api.curseforge.com/v1/rewards",
]
for u in cf_rp:
    try:
        r = urllib.request.Request(u, headers={"x-api-key": CF_KEY})
        r.add_header("User-Agent", "fliflight-report/1.0")
        with urllib.request.urlopen(r, timeout=20) as resp:
            out["revenue_probe"][u] = {"status": resp.status, "body": resp.read().decode()[:300]}
    except Exception as e:
        out["revenue_probe"][u] = {"error": str(e)}

mr_rp = [
    f"/v2/user/{MR_USER}/payouts",
    f"/v2/user/{MR_USER}/monetization",
]
for c in mr_rp:
    u = "https://api.modrinth.com" + c
    try:
        r = urllib.request.Request(u, headers={"Authorization": MR_TOKEN})
        r.add_header("User-Agent", "fliflight-report/1.0")
        with urllib.request.urlopen(r, timeout=20) as resp:
            out["revenue_probe"][u] = {"status": resp.status, "body": resp.read().decode()[:300]}
    except Exception as e:
        out["revenue_probe"][u] = {"error": str(e)}

print(json.dumps(out, indent=2, ensure_ascii=False))
