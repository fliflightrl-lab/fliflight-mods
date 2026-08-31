import requests, json

CF_KEY = "$2a$10$Uvg9i4yTuWKGujo0hQbVaOvOb9i1b2QqikOmDB2pEk2hACZE5n08O"
CF_HDRS = {"x-api-key": CF_KEY, "Accept": "application/json"}

# Search CF for the author's mods to get a complete list
url = "https://api.curseforge.com/v1/mods/search?gameId=432&searchFilter=Fliflightmc&pageSize=50"
r = requests.get(url, headers=CF_HDRS, timeout=30)
print("HTTP", r.status_code)
d = r.json()
data = d.get("data", [])
print("pagination totalCount:", d.get("pagination", {}).get("totalCount"))
print("returned:", len(data))
print()
for m in data:
    authors = [a.get("name") for a in m.get("authors", [])]
    print(f"{m['id']:8} | dl={m.get('downloadCount',0):6} | classId={m.get('classId')} | {m['name'][:55]} | authors={authors}")
