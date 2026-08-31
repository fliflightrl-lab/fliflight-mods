import json, urllib.request, urllib.parse, sys, os

CF_KEY = "$2a$10$Uvg9i4yTuWKGujo0hQbVaOvOb9i1b2QqikOmDB2pEk2hACZE5n08O"
MR_TOKEN = "mrp_BuW9lcEew20QyOIPdCxYhx6APN5bCh0usOZbSycTsNHlmm2jhiFOrR3GOeLI"
MR_USER = "sG9DNUJw"
CF_AUTHOR = 123880127

def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    req.add_header("User-Agent", "fliflight-report/1.0")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

out = {}

# --- Modrinth: full user project list ---
try:
    mr = get(f"https://api.modrinth.com/v2/user/{MR_USER}/projects",
             {"Authorization": MR_TOKEN})
    out["modrinth_projects"] = mr
except Exception as e:
    out["modrinth_error"] = str(e)

# --- Modrinth user object (has download totals? check) ---
try:
    u = get(f"https://api.modrinth.com/v2/user/{MR_USER}", {"Authorization": MR_TOKEN})
    out["modrinth_user"] = u
except Exception as e:
    out["modrinth_user_error"] = str(e)

# --- CurseForge: author search ---
try:
    q = urllib.parse.quote("Fliflightmc")
    cf = get(f"https://api.curseforge.com/v1/mods/search?gameId=432&searchFilter={q}&pageSize=50",
             {"x-api-key": CF_KEY})
    out["cf_search"] = cf
except Exception as e:
    out["cf_search_error"] = str(e)

print(json.dumps(out, indent=2, ensure_ascii=False))
