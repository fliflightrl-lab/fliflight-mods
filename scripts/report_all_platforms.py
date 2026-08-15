#!/usr/bin/env python3
"""Full cross-platform download/revenue report for Fliflightmc.
Gathers CurseForge downloads (read API), Modrinth downloads+followers (public API),
and GitHub Releases downloads, then prints a consolidated French report JSON/text."""
import json, os, sys
import urllib.request

HOME = os.path.expanduser("~")
CREDS = os.path.join(HOME, ".config", "fliflightmc", "credentials.json")
BASELINE = os.path.join(HOME, ".config", "fliflightmc", "cf_downloads_baseline.json")

CF_KEY = json.load(open(CREDS, encoding="utf-8"))["curseforge"]["api_key"]
GH_REPO = "fliflightrl-lab/fliflight-mods"

# canonical catalog: (label, cf_id, modrinth_id)
PACKS = [
    ("Dot Crosshair",            1499007, "4r8Ufv9p"),
    ("CrossX Crosshair",         1499029, "1ylCihJa"),
    ("Better Crosshair",         1494020, "oBGsX8oY"),
    ("Bigger Dot Crosshair",     1499072, "d8t14H03"),
    ("CrosshairX",               1497428, "Y8zhQ9z5"),
    ("Sniper Crosshair",         1588694, "4JKFVXUw"),
    ("Crossy Crosshair",         1558798, "sQkn3uEf"),
    ("Visible Ores",             1334611, "SEfn6MDy"),
    ("Short Sword",              1334714, "IcIJjhMO"),
    ("Diamond Dimension",        1479652, "NR54mkOD"),
    ("Clear Pumpkin",            1653159, "xnQODGjN"),
    ("Low Fire",                 1653138, "RIH3vxZQ"),
    ("PvP Essentials (flagship)", 1653188, "cHpwGcrb"),
]


def get(url, headers=None, timeout=30):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def cf_downloads(cid):
    d = get(f"https://api.curseforge.com/v1/mods/{cid}", {"x-api-key": CF_KEY})
    return d["data"]["downloadCount"]


def mr_project(mid):
    return get(f"https://api.modrinth.com/v2/project/{mid}", {"User-Agent": "fliflight-report/1.0"})


def gh_releases():
    try:
        rels = get(f"https://api.github.com/repos/{GH_REPO}/releases?per_page=100",
                   {"User-Agent": "fliflight-report/1.0", "Accept": "application/vnd.github+json"})
    except Exception as e:
        return None, str(e)
    total = 0
    per_rel = []
    for r in rels:
        dls = sum(a.get("download_count", 0) for a in r.get("assets", []))
        total += dls
        per_rel.append({"tag": r.get("tag_name"), "downloads": dls})
    return {"total": total, "releases": per_rel}, None


def main():
    prev = json.load(open(BASELINE, encoding="utf-8")) if os.path.exists(BASELINE) else {}

    cf_rows = []
    mr_rows = []
    for label, cid, mid in PACKS:
        # CurseForge
        try:
            cdl = cf_downloads(cid)
            pdl = prev.get(str(cid), {}).get("downloads", cdl)
            cf_rows.append({"label": label, "cf_id": cid, "cf_downloads": cdl,
                            "cf_delta": cdl - pdl})
        except Exception as e:
            cf_rows.append({"label": label, "cf_id": cid, "cf_downloads": None,
                            "cf_delta": None, "error": str(e)})
        # Modrinth
        try:
            p = mr_project(mid)
            mr_rows.append({"label": label, "mr_id": mid,
                            "mr_downloads": p.get("downloads"),
                            "mr_followers": p.get("followers"),
                            "mr_status": p.get("status")})
        except Exception as e:
            mr_rows.append({"label": label, "mr_id": mid,
                            "mr_downloads": None, "mr_followers": None, "error": str(e)})

    gh, gh_err = gh_releases()

    cf_total = sum(r["cf_downloads"] for r in cf_rows if r["cf_downloads"] is not None)
    cf_delta = sum(r["cf_delta"] for r in cf_rows if r["cf_delta"] is not None)
    mr_total = sum(r["mr_downloads"] for r in mr_rows if r["mr_downloads"] is not None)
    mr_follow = sum(r["mr_followers"] for r in mr_rows if r["mr_followers"] is not None)

    result = {
        "curseforge": {"rows": cf_rows, "total": cf_total, "delta": cf_delta},
        "modrinth": {"rows": mr_rows, "total": mr_total, "followers": mr_follow},
        "github": gh,
        "github_error": gh_err,
    }
    out = os.path.join(HOME, ".config", "fliflightmc", "report_all_platforms.json")
    json.dump(result, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
