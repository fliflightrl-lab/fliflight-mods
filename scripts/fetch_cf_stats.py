#!/usr/bin/env python3
"""Fetch CurseForge stats via the read API and generate a self-contained portfolio
site (site/index.html) with the data embedded (no server needed).

Usage: python3 scripts/fetch_cf_stats.py
Revenue: actual payout (from your Rewards dashboard) goes in
         ~/.config/fliflightmc/revenue.json  {"actual_revenue_usd": 123.45}
"""
import base64, datetime, json, os, time

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
CREDS = os.path.expanduser("~/.config/fliflightmc/credentials.json")
REVENUE_FILE = os.path.expanduser("~/.config/fliflightmc/revenue.json")

REVENUE_RATE_PER_1K = 2.0  # USD estimé / 1000 téléchargements (ajuster au taux réel)
AUTHOR_ID = 123880127
GAME_ID = 432
API = "https://api.curseforge.com/v1"

# Real numbers from the CurseForge dashboard (video showreel) — NOT exposed by the API.
DASHBOARD = {
    "total_downloads": 129873,
    "per_day": 800,
    "revenue_month_eur": 100,
    "projects": 19,
    "packs": 16,
    "mods": 3,
    "flagship": {"name": "Dot Crosshair", "downloads": 33068},
}


def mr_map():
    """cf_id -> (modrinth_id, slug) from the local manifests."""
    m = {}
    packs = os.path.join(ROOT, "packs")
    if os.path.isdir(packs):
        for slug in os.listdir(packs):
            mp = os.path.join(packs, slug, "manifest.json")
            if os.path.exists(mp):
                d = json.load(open(mp, encoding="utf-8"))
                m[d["curseforge_id"]] = d.get("modrinth_id"), slug
    return m


def get(url, h, params=None):
    """GET with retry — the CF read API returns intermittent 403s."""
    last = None
    for attempt in range(5):
        r = requests.get(url, params=params, headers=h, timeout=30)
        if r.status_code == 200:
            return r
        last = r
        time.sleep(1.5 * (attempt + 1))
    last.raise_for_status()


def fetch():
    key = json.load(open(CREDS, encoding="utf-8"))["curseforge"]["api_key"]
    h = {"x-api-key": key}
    r = get(f"{API}/mods/search", h, params={"gameId": GAME_ID, "authorId": AUTHOR_ID, "pageSize": 50})
    mods = r.json().get("data", [])
    mr = mr_map()

    projects = []
    for mod in mods:
        cid = mod["id"]
        # detail for logo/screenshots
        d = get(f"{API}/mods/{cid}", h).json().get("data", {})
        logo = (d.get("logo") or {}).get("thumbnailUrl") or (d.get("logo") or {}).get("url") or ""
        mr_id, slug = mr.get(cid, (None, None))
        projects.append({
            "name": mod["name"],
            "downloads": mod.get("downloadCount", 0),
            "rank": mod.get("gamePopularityRank"),
            "type": "mod" if mod.get("classId") == 6 else "resourcepack",
            "icon": logo,
            "cf_url": (mod.get("links") or {}).get("websiteUrl") or "",
            "mr_url": f"https://modrinth.com/project/{slug}" if slug else "",
            "released": (mod.get("dateReleased") or "")[:10],
        })
    projects.sort(key=lambda x: x["downloads"], reverse=True)
    total = sum(p["downloads"] for p in projects)

    actual = None
    if os.path.exists(REVENUE_FILE):
        actual = json.load(open(REVENUE_FILE, encoding="utf-8")).get("actual_revenue_usd")

    return {
        "generated_at": datetime.datetime.now().isoformat(),
        "total_downloads": total,
        "project_count": len(projects),
        "mod_count": sum(1 for p in projects if p["type"] == "mod"),
        "resourcepack_count": sum(1 for p in projects if p["type"] == "resourcepack"),
        "top_pack": {"name": projects[0]["name"], "downloads": projects[0]["downloads"]} if projects else {"name": "", "downloads": 0},
        "estimated_revenue_usd": round(total / 1000.0 * REVENUE_RATE_PER_1K, 2),
        "revenue_rate_per_1k": REVENUE_RATE_PER_1K,
        "actual_revenue_usd": actual,
        "dashboard": DASHBOARD,
        "projects": projects,
    }


def main():
    cache = os.path.join(SITE, "cache.json")
    try:
        payload = fetch()
        json.dump(payload, open(cache, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    except Exception as e:
        print(f"API indisponible ({e}) — utilisation du cache local {cache}")
        if os.path.exists(cache):
            payload = json.load(open(cache, encoding="utf-8"))
        else:
            raise SystemExit("Pas de cache et API HS : lance d'abord scripts/build_cache.py")
    # inline local icons as base64 so the HTML is fully self-contained
    for p in payload["projects"]:
        ic = p.get("icon") or ""
        if ic.startswith("assets/"):
            fp = os.path.join(SITE, ic)
            if os.path.exists(fp):
                ext = ic.rsplit(".", 1)[-1].lower()
                mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
                p["icon"] = f"data:{mime};base64," + base64.b64encode(open(fp, "rb").read()).decode()
    tpl = open(os.path.join(SITE, "template.html"), encoding="utf-8").read()
    html = tpl.replace("__CF_DATA__", json.dumps(payload, ensure_ascii=False))
    out = os.path.join(SITE, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"OK -> {out}")
    print(f"  {payload['project_count']} projets, {payload['total_downloads']:,} téléchargements, "
          f"estimé ${payload['estimated_revenue_usd']} ({payload['revenue_rate_per_1k']} $/1k)")


if __name__ == "__main__":
    main()
