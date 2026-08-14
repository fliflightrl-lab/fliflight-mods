#!/usr/bin/env python3
"""
Consolidation: prepend a "consolidated into Dot Crosshair" banner to the 6
secondary crosshair packs (manifests + live Modrinth), so their traffic funnels
into the flagship. Reversible: delete the banner line to undo.

Usage: python3 scripts/apply_archive.py
"""
import json, os

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS = os.path.join(ROOT, "packs")
CREDS = os.path.expanduser("~/.config/fliflightmc/credentials.json")
MR_API = "https://api.modrinth.com/v2"

DOT_CF = "https://www.curseforge.com/minecraft/texture-packs/dot-crosshair-cossx-better-crosshair"
BANNER = (f"> **📌 Consolidated:** this crosshair is now part of the "
          f"**[Dot Crosshair]({DOT_CF})** flagship — get the latest version there.\n\n")

SECONDARY = [
    "crossx-crossx-better-crosshair",
    "crossx-better-crosshair",
    "bigger-dot-crosshair-cossx-better-crosshair",
    "crosshairx-better-crosshair",
    "crossx",  # sniper
    "crossy-crossx-better-crosshair",
]


def main():
    token = json.load(open(CREDS, encoding="utf-8"))["modrinth"]["token"]
    n = 0
    for slug in SECONDARY:
        mp = os.path.join(PACKS, slug, "manifest.json")
        m = json.load(open(mp, encoding="utf-8"))
        body = m.get("body", "")
        if body.startswith("> **📌 Consolidated:"):
            print(f"SKIP {slug} (déjà banné)")
            continue
        m["body"] = BANNER + body
        json.dump(m, open(mp, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        r = requests.patch(f"{MR_API}/project/{m['modrinth_id']}",
                           headers={"Authorization": token}, json={"body": m["body"]}, timeout=60)
        print(f"{slug} -> manifest + PATCH {m['modrinth_id']} = {r.status_code}")
        n += 1
    print(f"\nDone: {n} packs bannés (consolidation vers Dot Crosshair).")


if __name__ == "__main__":
    main()
