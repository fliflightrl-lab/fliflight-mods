import requests, json

MR_TOKEN = "mrp_BuW9lcEew20QyOIPdCxYhx6APN5bCh0usOZbSycTsNHlmm2jhiFOrR3GOeLI"
MR_USER = "sG9DNUJw"
MR_HDRS = {"Authorization": MR_TOKEN, "User-Agent": "fliflight/1.0"}

candidates = [
    f"/v2/user/{MR_USER}/payouts",
    f"/v2/user/{MR_USER}/payouts/balance",
    f"/v2/user/{MR_USER}/monetization",
    f"/v2/user/{MR_USER}/payout_balance",
    f"/v2/user/{MR_USER}/revenue",
    f"/v2/organization/{MR_USER}/payouts",
    "/v2/user/{id}/payouts".replace("{id}", MR_USER),
]
for c in candidates:
    try:
        r = requests.get("https://api.modrinth.com" + c, headers=MR_HDRS, timeout=20)
        print(f"{c} -> {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"{c} -> ERR {e}")
