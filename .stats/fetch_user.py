import requests, json

MR_TOKEN = "mrp_BuW9lcEew20QyOIPdCxYhx6APN5bCh0usOZbSycTsNHlmm2jhiFOrR3GOeLI"
MR_USER = "sG9DNUJw"
MR_HDRS = {"Authorization": MR_TOKEN, "User-Agent": "fliflight/1.0 (fliflight.rl@gmail.com)"}

def show(label, r):
    print(f"\n### {label} -> HTTP {r.status_code}")
    try:
        print(json.dumps(r.json(), indent=2, ensure_ascii=False)[:4000])
    except Exception:
        print(r.text[:2000])

# Full list of Modrinth projects for the user
show("GET /v2/user/{id}/projects", requests.get(f"https://api.modrinth.com/v2/user/{MR_USER}/projects", headers=MR_HDRS, timeout=30))

# User object (monetization info)
show("GET /v2/user/{id}", requests.get(f"https://api.modrinth.com/v2/user/{MR_USER}", headers=MR_HDRS, timeout=30))

# Payouts / monetization
show("GET /v2/user/{id}/payouts", requests.get(f"https://api.modrinth.com/v2/user/{MR_USER}/payouts", headers=MR_HDRS, timeout=30))
show("GET /v2/user/{id}/payouts/balance", requests.get(f"https://api.modrinth.com/v2/user/{MR_USER}/payouts/balance", headers=MR_HDRS, timeout=30))
