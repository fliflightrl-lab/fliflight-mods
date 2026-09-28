import json, urllib.request

CF_KEY = "$2a$10$Uvg9i4yTuWKGujo0hQbVaOvOb9i1b2QqikOmDB2pEk2hACZE5n08O"
CF_AUTHOR = 123880127
MR_TOKEN = "mrp_BuW9lcEew20QyOIPdCxYhx6APN5bCh0usOZbSycTsNHlmm2jhiFOrR3GOeLI"
MR_USER = "sG9DNUJw"

def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    return json.load(urllib.request.urlopen(req, timeout=30))

# CurseForge search
cf_mods = []
page = 0
while True:
    url = f"https://api.curseforge.com/v1/mods/search?gameId=432&searchFilter=Fliflightmc&pageSize=50&index={page*50}"
    r = get(url, {"x-api-key": CF_KEY})
    data = r["data"]
    for m in data:
        authors = m.get("authors", [])
        if any(a.get("id") == CF_AUTHOR for a in authors):
            cf_mods.append(m)
    if len(data) < 50:
        break
    page += 1

print("=== CURSEFORGE MODS ===")
print("count:", len(cf_mods))
for m in cf_mods:
    print(json.dumps({"id": m["id"], "name": m["name"], "classId": m.get("classId"), "downloads": m.get("downloadCount"), "slug": m.get("slug")}))

# Modrinth projects
mr = get(f"https://api.modrinth.com/v2/user/{MR_USER}/projects", {"Authorization": MR_TOKEN})
print("\n=== MODRINTH PROJECTS ===")
print("count:", len(mr))
for p in mr:
    print(json.dumps({"id": p["id"], "slug": p["slug"], "type": p.get("project_type"), "downloads": p.get("downloads"), "followers": p.get("followers")}))
