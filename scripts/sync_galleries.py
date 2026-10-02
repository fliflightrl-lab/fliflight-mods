#!/usr/bin/env python3
"""Mirror each CurseForge project's first N screenshots into the matching Modrinth
project gallery (replacing whatever is currently there).

Usage: python3 scripts/sync_galleries.py [--max 3] [--dry-run]
"""
import argparse, json, os, urllib.parse

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS = os.path.join(ROOT, "packs")
CREDS = os.path.expanduser("~/.config/fliflightmc/credentials.json")
CF_API = "https://api.curseforge.com/v1"
MR_API = "https://api.modrinth.com/v2"
UA = {"User-Agent": "Mozilla/5.0 (FliflightMC gallery sync)"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    c = json.load(open(CREDS, encoding="utf-8"))
    cfh = {"x-api-key": c["curseforge"]["api_key"]}
    mrh = {"Authorization": c["modrinth"]["token"]}

    cf2mr = {}
    for slug in os.listdir(PACKS):
        mp = os.path.join(PACKS, slug, "manifest.json")
        if os.path.exists(mp):
            m = json.load(open(mp, encoding="utf-8"))
            cf2mr[m["curseforge_id"]] = (m.get("modrinth_id"), slug)

    mods = requests.get(f"{CF_API}/mods/search",
                        params={"gameId": 432, "authorId": 123880127, "pageSize": 50},
                        headers=cfh, timeout=30).json()["data"]

    for mod in mods:
        cid = mod["id"]
        if cid not in cf2mr:
            continue
        mrid, slug = cf2mr[cid]
        if not mrid:
            print(f"SKIP {slug}: pas de projet Modrinth")
            continue
        d = requests.get(f"{CF_API}/mods/{cid}", headers=cfh, timeout=30).json()["data"]
        shots = [s.get("url") for s in d.get("screenshots", []) if s.get("url")][:args.max]
        if not shots:
            print(f"SKIP {slug}: 0 capture CF")
            continue

        proj = requests.get(f"{MR_API}/project/{mrid}", headers=mrh, timeout=30).json()
        cur = [g["url"] for g in proj.get("gallery", [])]
        print(f"{slug}: {len(cur)} image(s) actuelle(s) -> {len(shots)} capture(s) CF")

        if args.dry_run:
            continue
        # 1) delete existing gallery
        for u in cur:
            r = requests.delete(f"{MR_API}/project/{mrid}/gallery",
                                params={"url": u}, headers=mrh, timeout=30)
            print(f"   del {r.status_code}")
        # 2) upload CF screenshots
        for i, url in enumerate(shots):
            data = requests.get(url, headers=UA, timeout=60).content
            ext = "png" if url.lower().endswith(".png") else "jpg"
            mime = "image/png" if ext == "png" else "image/jpeg"
            r = requests.post(f"{MR_API}/project/{mrid}/gallery",
                              params={"ext": ext, "featured": "false", "ordering": i},
                              headers={**mrh, "Content-Type": mime}, data=data, timeout=90)
            print(f"   add[{i}] {r.status_code} {len(data)}B {url[-40:]}")
    print("\nDONE")


if __name__ == "__main__":
    main()
