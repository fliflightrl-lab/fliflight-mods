import requests, json, sys, time

CF_KEY = "$2a$10$Uvg9i4yTuWKGujo0hQbVaOvOb9i1b2QqikOmDB2pEk2hACZE5n08O"
MR_TOKEN = "mrp_BuW9lcEew20QyOIPdCxYhx6APN5bCh0usOZbSycTsNHlmm2jhiFOrR3GOeLI"
MR_USER = "sG9DNUJw"

CF_HDRS = {"x-api-key": CF_KEY, "Accept": "application/json"}
MR_HDRS = {"Authorization": MR_TOKEN, "User-Agent": "fliflight/1.0 (fliflight.rl@gmail.com)"}

# List of all projects (from manifests) with both ids
projects = [
    ("Diamond Dimension", 1479652, "NR54mkOD", "mod"),
    ("Bigger Dot Crosshair", 1499072, "d8t14H03", "resourcepack"),
    ("CrosshairX", 1497428, "Y8zhQ9z5", "resourcepack"),
    ("Sniper Crosshair", 1588694, "4JKFVXUw", "resourcepack"),
    ("Better Crosshair", 1494020, "oBGsX8oY", "resourcepack"),
    ("CrossX Crosshair", 1499029, "1ylCihJa", "resourcepack"),
    ("Crossy Crosshair", 1558798, "sQkn3uEf", "resourcepack"),
    ("Dot Crosshair", 1499007, "4r8Ufv9p", "resourcepack"),
    ("Clear Pumpkin", 1653159, "xnQODGjN", "resourcepack"),
    ("Low Fire", 1653138, "RIH3vxZQ", "resourcepack"),
    ("PvP Essentials", 1653188, "cHpwGcrb", "resourcepack"),
    ("Short Sword", 1334714, "IcIJjhMO", "resourcepack"),
    ("Visible Ores", 1334611, "SEfn6MDy", "resourcepack"),
]

results = []

for name, cfid, mrid, ptype in projects:
    row = {"name": name, "cf_id": cfid, "mr_id": mrid, "type": ptype}
    # CurseForge
    try:
        r = requests.get(f"https://api.curseforge.com/v1/mods/{cfid}", headers=CF_HDRS, timeout=30)
        if r.status_code == 200:
            d = r.json()["data"]
            row["cf_downloads"] = d.get("downloadCount")
            row["cf_name"] = d.get("name")
        else:
            row["cf_error"] = f"HTTP {r.status_code}"
    except Exception as e:
        row["cf_error"] = str(e)
    time.sleep(0.4)

    # Modrinth project
    try:
        r = requests.get(f"https://api.modrinth.com/v2/project/{mrid}", headers=MR_HDRS, timeout=30)
        if r.status_code == 200:
            d = r.json()
            row["mr_downloads"] = d.get("downloads")
            row["mr_followers"] = d.get("followers")
            row["mr_title"] = d.get("title")
        else:
            row["mr_error"] = f"HTTP {r.status_code}"
    except Exception as e:
        row["mr_error"] = str(e)
    time.sleep(0.4)
    results.append(row)
    print(json.dumps(row, ensure_ascii=False))

with open("cf_mr_projects.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("\nSaved cf_mr_projects.json")
