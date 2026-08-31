import requests, json

MR_TOKEN = "mrp_BuW9lcEew20QyOIPdCxYhx6APN5bCh0usOZbSycTsNHlmm2jhiFOrR3GOeLI"
MR_USER = "sG9DNUJw"
MR_HDRS = {"Authorization": MR_TOKEN, "User-Agent": "fliflight/1.0"}

r = requests.get(f"https://api.modrinth.com/v2/user/{MR_USER}/projects", headers=MR_HDRS, timeout=30)
projects = r.json()
print(f"Total Modrinth projects: {len(projects)}\n")
for p in projects:
    print(f"{p['id']:12} | {p['project_type']:13} | dl={p['downloads']:6} | followers={p['followers']:3} | monet={p.get('monetization_status')} | {p['title']}")
