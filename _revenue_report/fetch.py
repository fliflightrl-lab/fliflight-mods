import json, urllib.request, urllib.parse, sys, time

CF_KEY = "$2a$10$Uvg9i4yTuWKGujo0hQbVaOvOb9i1b2QqikOmDB2pEk2hACZE5n08O"
MR_TOKEN = "mrp_BuW9lcEew20QyOIPdCxYhx6APN5bCh0usOZbSycTsNHlmm2jhiFOrR3GOeLI"
MR_USER = "sG9DNUJw"
CF_AUTHOR = "Fliflightmc"

def get(url, headers):
    req = urllib.request.Request(url, headers=headers)
    req.add_header("User-Agent", "fliflight-report/1.0")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

# ---- CurseForge: list mods by author ----
cf_headers = {"x-api-key": CF_KEY}
all_mods = []
index = 0
page_size = 50
while True:
    url = f"https://api.curseforge.com/v1/mods/search?gameId=432&searchFilter={urllib.parse.quote(CF_AUTHOR)}&pageSize={page_size}&index={index}"
    d = get(url, cf_headers)
    data = d.get("data", [])
    total = d.get("pagination", {}).get("totalCount", 0)
    for m in data:
        authors = m.get("authors", [])
        names = [a.get("name","") for a in authors]
        all_mods.append({
            "id": m.get("id"),
            "name": m.get("name"),
            "downloadCount": m.get("downloadCount", 0),
            "slug": m.get("slug"),
            "classId": m.get("classId"),
            "authors": names,
        })
    index += page_size
    if index >= total or not data:
        break

# filter to actual author
cf_mods = [m for m in all_mods if CF_AUTHOR in m["authors"]]

# ---- Modrinth: list projects by user ----
mr_headers = {"Authorization": MR_TOKEN}
mr_projects = get(f"https://api.modrinth.com/v2/user/{MR_USER}/projects", mr_headers)

out = {
    "curseforge": cf_mods,
    "modrinth": [
        {
            "id": p.get("id"),
            "title": p.get("title"),
            "slug": p.get("slug"),
            "project_type": p.get("project_type"),
            "downloads": p.get("downloads", 0),
            "followers": p.get("followers", 0),
        }
        for p in mr_projects
    ],
}

print(json.dumps(out, ensure_ascii=False, indent=2))
