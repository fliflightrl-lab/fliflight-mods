#!/usr/bin/env python3
"""One-time seed of site/cache.json from the local manifests + a snapshot of the
last-known CurseForge download counts (used as fallback when the CF API is 403'd).

Also copies each pack's icon into site/assets/ so the site is self-contained.
"""
import datetime, json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
PACKS = os.path.join(ROOT, "packs")
ASSETS = os.path.join(SITE, "assets")

# cf_id -> (downloads, rank, released)  — last known snapshot
SNAPSHOT = {
    1499007: (24825, 16146, "2026-03-29"),
    1499029: (14656, 18290, "2026-03-29"),
    1334611: (13120, 25107, "2025-08-25"),
    1494020: (8122, 22815, "2026-03-23"),
    1499072: (6476, 25148, "2026-03-29"),
    1334714: (5744, 31924, "2025-08-25"),
    1497428: (5135, 28585, "2026-03-28"),
    1588694: (3942, 999999, "2026-06-26"),
    1558798: (2204, 999999, "2026-05-30"),
    1479652: (674, 55235, "2026-03-07"),
    1653159: (186, None, ""),
    1653138: (185, None, ""),
    1653188: (14, None, ""),
}
RATE = 2.0


def main():
    os.makedirs(ASSETS, exist_ok=True)
    projects = []
    if os.path.isdir(PACKS):
        for slug in os.listdir(PACKS):
            mp = os.path.join(PACKS, slug, "manifest.json")
            if not os.path.exists(mp):
                continue
            m = json.load(open(mp, encoding="utf-8"))
            cid = m["curseforge_id"]
            dl, rank, rel = SNAPSHOT.get(cid, (0, None, ""))
            icon = ""
            for ext in ("png", "jpg", "jpeg"):
                src = os.path.join(PACKS, slug, f"icon.{ext}")
                if os.path.exists(src):
                    dst = os.path.join(ASSETS, f"{slug}.{ext}")
                    shutil.copy(src, dst)
                    icon = f"assets/{slug}.{ext}"
                    break
            projects.append({
                "name": m["name"],
                "downloads": dl,
                "rank": rank,
                "type": m["project_type"],
                "icon": icon,
                "cf_url": (m.get("links") or {}).get("website_url") or "",
                "mr_url": f"https://modrinth.com/project/{slug}",
                "released": rel,
            })

    projects.sort(key=lambda x: x["downloads"], reverse=True)
    total = sum(p["downloads"] for p in projects)
    payload = {
        "generated_at": datetime.datetime.now().isoformat(),
        "total_downloads": total,
        "project_count": len(projects),
        "mod_count": sum(1 for p in projects if p["type"] == "mod"),
        "resourcepack_count": sum(1 for p in projects if p["type"] == "resourcepack"),
        "top_pack": {"name": projects[0]["name"], "downloads": projects[0]["downloads"]},
        "estimated_revenue_usd": round(total / 1000.0 * RATE, 2),
        "revenue_rate_per_1k": RATE,
        "actual_revenue_usd": None,
        "projects": projects,
    }
    json.dump(payload, open(os.path.join(SITE, "cache.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"cache.json -> {len(projects)} projets, {total:,} dl, "
          f"${payload['estimated_revenue_usd']} estimé ; icônes copiées dans {ASSETS}")


if __name__ == "__main__":
    main()
