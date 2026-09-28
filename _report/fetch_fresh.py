import json, urllib.request, urllib.parse, time

CF_KEY = "$2a$10$Uvg9i4yTuWKGujo0hQbVaOvOb9i1b2QqikOmDB2pEk2hACZE5n08O"
MR_TOKEN = "mrp_BuW9lcEew20QyOIPdCxYhx6APN5bCh0usOZbSycTsNHlmm2jhiFOrR3GOeLI"
MR_USER = "sG9DNUJw"
CF_AUTHOR = "Fliflightmc"

def get(url, headers=None, raw=False):
    req = urllib.request.Request(url, headers=headers or {})
    req.add_header("User-Agent", "fliflight-report/1.0")
    with urllib.request.urlopen(req, timeout=60) as r:
        b = r.read()
        return b if raw else json.loads(b.decode("utf-8"))

out = {}

# ---- CurseForge: paginated author search ----
cf_mods = []
index = 0
page_size = 50
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
                "id": m.get("id"),
                "name": m.get("name"),
                "downloadCount": m.get("downloadCount", 0),
                "slug": m.get("slug"),
                "classId": m.get("classId"),
                "summary": m.get("summary"),
                "authors": names,
            })
    index += page_size
    if index >= total or not data:
        break
out["curseforge"] = cf_mods

# ---- Modrinth projects ----
mr_projects = get(f"https://api.modrinth.com/v2/user/{MR_USER}/projects",
                  {"Authorization": MR_TOKEN})
out["modrinth"] = [
    {
        "id": p.get("id"),
        "title": p.get("title"),
        "slug": p.get("slug"),
        "project_type": p.get("project_type"),
        "downloads": p.get("downloads", 0),
        "followers": p.get("followers", 0),
    }
    for p in mr_projects
]

# ---- Modrinth user object (total downloads / any earnings) ----
try:
    u = get(f"https://api.modrinth.com/v2/user/{MR_USER}", {"Authorization": MR_TOKEN})
    out["modrinth_user"] = u
except Exception as e:
    out["modrinth_user_error"] = str(e)

# ---- GitHub releases/downloads ----
out["github"] = {}
try:
    gh = get("https://api.github.com/repos/fliflightrl-lab/fliflight-mods")
    out["github"]["repo"] = {
        "stargazers": gh.get("stargazers_count"),
        "forks": gh.get("forks_count"),
        "open_issues": gh.get("open_issues_count"),
    }
    rels = get("https://api.github.com/repos/fliflightrl-lab/fliflight-mods/releases?per_page=100")
    gh_releases = []
    for r in rels:
        assets = r.get("assets", [])
        dl = sum(a.get("download_count", 0) for a in assets)
        gh_releases.append({"tag": r.get("tag_name"), "downloads": dl,
                            "assets": len(assets)})
    out["github"]["releases"] = gh_releases
except Exception as e:
    out["github"]["error"] = str(e)

print(json.dumps(out, indent=2, ensure_ascii=False))
