import json, urllib.request, urllib.parse

CF_KEY = "$2a$10$Uvg9i4yTuWKGujo0hQbVaOvOb9i1b2QqikOmDB2pEk2hACZE5n08O"
MR_TOKEN = "mrp_BuW9lcEew20QyOIPdCxYhx6APN5bCh0usOZbSycTsNHlmm2jhiFOrR3GOeLI"
MR_USER = "sG9DNUJw"

def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    req.add_header("User-Agent", "fliflight-report/1.0")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

# Modrinth
mr = get(f"https://api.modrinth.com/v2/user/{MR_USER}/projects", {"Authorization": MR_TOKEN})
print("MODRINTH PROJECTS:", len(mr))
for p in sorted(mr, key=lambda x: -x["downloads"]):
    print(f"  {p['downloads']:>6} dl  {p['followers']:>3} fol  {p['monetization_status']:<10} {p['project_type']:<12} {p['id']}  {p['title']}")

# Modrinth user
try:
    u = get(f"https://api.modrinth.com/v2/user/{MR_USER}", {"Authorization": MR_TOKEN})
    print("\nMODRINTH USER KEYS:", sorted(u.keys()))
    for k in ("username","id","email_verified","role","payout_data","monetization_status","organization"):
        if k in u:
            print(f"  {k}: {u[k]}")
except Exception as e:
    print("user err", e)

# CurseForge search
q = urllib.parse.quote("Fliflightmc")
cf = get(f"https://api.curseforge.com/v1/mods/search?gameId=432&searchFilter={q}&pageSize=50", {"x-api-key": CF_KEY})
print("\nCURSEFORGE SEARCH totalCount:", cf["pagination"]["totalCount"])
mods = [m for m in cf["data"] if any(a.get("name")=="Fliflightmc" for a in m.get("authors",[]))]
print("CF mods by Fliflightmc:", len(mods))
for m in sorted(mods, key=lambda x: -x["downloadCount"]):
    print(f"  {m['downloadCount']:>8} dl  class={m['classId']:<3} id={m['id']}  {m['name']}")

# dump raw CF to file for later
json.dump(cf, open("cf_raw.json","w"), ensure_ascii=False)
json.dump(mr, open("mr_raw.json","w"), ensure_ascii=False)
