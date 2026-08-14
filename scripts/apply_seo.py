#!/usr/bin/env python3
"""
Apply the SEO rewrite (docs/optimisation/01-seo-et-consolidation.md) to:
  1. the local manifests (source of truth)
  2. the live Modrinth projects (PATCH /project/{id})

Usage:
  python3 scripts/apply_seo.py            # apply to manifests + Modrinth
  python3 scripts/apply_seo.py --manifest-only
"""
import argparse, json, os, sys

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS = os.path.join(ROOT, "packs")
CREDS = os.path.expanduser("~/.config/fliflightmc/credentials.json")
MR_API = "https://api.modrinth.com/v2"

CF = {
    "dot": "https://www.curseforge.com/minecraft/texture-packs/dot-crosshair-cossx-better-crosshair",
    "crossx": "https://www.curseforge.com/minecraft/texture-packs/crossx-crossx-better-crosshair",
    "bigger-dot": "https://www.curseforge.com/minecraft/texture-packs/bigger-dot-crosshair-cossx-better-crosshair",
    "sniper": "https://www.curseforge.com/minecraft/texture-packs/crossx-better-crosshair-sniper-crosshair",
    "ores": "https://www.curseforge.com/minecraft/texture-packs/visible-ores-all-versions-and-netherite",
    "sword": "https://www.curseforge.com/minecraft/texture-packs/pvp-sword-little-sword-all-versions",
}

CROSSHAIR_TEMPLATE = (
    "Replaces the default Minecraft crosshair with a cleaner, sharper design.\n\n"
    "**Compatible with all versions** (1.11 → latest) and works on every launcher.\n"
    "Just drop the pack in your `resourcepacks` folder and enable it — no Optifine required.\n"
    "Perfect for PvP, survival and bow aim."
)

SEO = {
    "dot-crosshair-cossx-better-crosshair": {
        "title": "Dot Crosshair — Clean PvP & Survival Crosshair (All Versions)",
        "summary": "A minimal dot crosshair that declutters your screen for PvP and survival. Works from 1.11 to the latest version.",
        "body": CROSSHAIR_TEMPLATE + "\n\n---\n\n**More crosshairs from the CrossX series:** "
                f"[Bigger Dot]({CF['bigger-dot']}) · [CrossX]({CF['crossx']}) · [Sniper]({CF['sniper']})\n"
                f"**Also try:** [Visible Ores]({CF['ores']}) · [Short Sword]({CF['sword']})",
    },
    "crossx-crossx-better-crosshair": {
        "title": "CrossX Crosshair — Custom PvP Crosshair Pack",
        "summary": "The original CrossX crosshair — a custom design that sharpens your aim in PvP and survival.",
        "body": CROSSHAIR_TEMPLATE + f"\n\n---\n\nPart of the **CrossX series**. Original & most popular: [Dot Crosshair]({CF['dot']})",
    },
    "crossx-better-crosshair": {
        "title": "Better Crosshair — Modern Clean Crosshair for PvP",
        "summary": "A modern, clean crosshair replacing the vanilla default with a sharper design seen in competitive games.",
        "body": CROSSHAIR_TEMPLATE + f"\n\n---\n\nPart of the **CrossX series**. Original & most popular: [Dot Crosshair]({CF['dot']})",
    },
    "bigger-dot-crosshair-cossx-better-crosshair": {
        "title": "Bigger Dot Crosshair — High-Visibility PvP Crosshair",
        "summary": "A larger, easy-to-see dot crosshair for precision without squinting — great for PvP and bow aim.",
        "body": CROSSHAIR_TEMPLATE + f"\n\n---\n\nPart of the **CrossX series**. Original & most popular: [Dot Crosshair]({CF['dot']})",
    },
    "crosshairx-better-crosshair": {
        "title": "CrosshairX — Enhanced Crosshair for PvP",
        "summary": "An enhanced crosshair with better visibility for fast-paced PvP fights.",
        "body": CROSSHAIR_TEMPLATE + f"\n\n---\n\nPart of the **CrossX series**. Original & most popular: [Dot Crosshair]({CF['dot']})",
    },
    "crossx": {  # sniper
        "title": "Sniper Crosshair — Precision for Bow & Long-Range PvP",
        "summary": "A sniper-style crosshair built for long-range shots and bow combat in PvP.",
        "body": CROSSHAIR_TEMPLATE + f"\n\n---\n\nPart of the **CrossX series**. Original & most popular: [Dot Crosshair]({CF['dot']})",
    },
    "crossy-crossx-better-crosshair": {
        "title": "Crossy Crosshair — Stylish PvP Crosshair",
        "summary": "A stylish crosshair variant for players who want a different look in PvP.",
        "body": CROSSHAIR_TEMPLATE + f"\n\n---\n\nPart of the **CrossX series**. Original & most popular: [Dot Crosshair]({CF['dot']})",
    },
    "visible-ores-all-versions-and-netherite": {
        "title": "Visible Ores — See Every Ore & Netherite (Shaders Ready)",
        "summary": "Makes every ore and ancient debris stand out so you never miss diamonds. Optimized for Optifine and complementary shaders.",
        "body": "Makes every ore and ancient debris stand out so you never miss diamonds.\n\n"
                "**Works with Optifine and complementary shaders** for the best results.\n"
                "Covers coal, copper, iron, gold, redstone, lapis, diamond, emerald, nether gold "
                "and ancient debris — including deepslate variants.\n\n---\n\n"
                f"**PvP essentials:** [Dot Crosshair]({CF['dot']}) · [Short Sword]({CF['sword']})",
    },
    "pvp-sword-little-sword-all-versions": {
        "title": "Short Sword — Smaller Swords for PvP (All Versions)",
        "summary": "Shrinks the oversized vanilla swords into compact PvP-friendly blades — less screen clutter, better visibility.",
        "body": "Shrinks the oversized vanilla swords into compact PvP-friendly blades.\n\n"
                "Covers wooden, stone, iron, golden, diamond and netherite swords.\n"
                "Less screen clutter, better visibility in fights.\n\n---\n\n"
                f"**Complete your PvP setup:** [Dot Crosshair]({CF['dot']}) · [Visible Ores]({CF['ores']})",
    },
    "all-in-diamonds-dimension": {
        "title": "Diamond Dimension — A New World Made of Diamonds (NeoForge)",
        "summary": "Craft a diamond portal and explore a whole dimension built from diamond blocks and mountains.",
        "body": "Craft a special lighter using 9 diamond blocks and a flint & steel, then right-click to "
                "open a portal to the Diamond Dimension. This dimension is made entirely of diamond — blocks, "
                "mountains, and even the ground. To return, step back through the portal.\n\n"
                "**Requires NeoForge.**\n\n---\n\n"
                f"**Looking for a resource pack?** [Visible Ores]({CF['ores']}) — see every ore clearly.",
    },
}


def load_creds():
    c = json.load(open(CREDS, encoding="utf-8"))
    return c.get("modrinth", {}).get("token")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest-only", action="store_true", help="update manifests only, skip Modrinth")
    args = ap.parse_args()

    token = None if args.manifest_only else load_creds()
    updated_manifests, patched = 0, 0

    for slug, seo in SEO.items():
        mp = os.path.join(PACKS, slug, "manifest.json")
        if not os.path.exists(mp):
            print(f"SKIP {slug}: manifest not found")
            continue
        m = json.load(open(mp, encoding="utf-8"))
        m["name"] = seo["title"]
        m["summary"] = seo["summary"]
        m["body"] = seo["body"]
        json.dump(m, open(mp, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        updated_manifests += 1
        print(f"[manifest] {slug} -> \"{seo['title']}\"")

        if token:
            r = requests.patch(f"{MR_API}/project/{m['modrinth_id']}",
                               headers={"Authorization": token},
                               json={"title": seo["title"], "description": seo["summary"], "body": seo["body"]},
                               timeout=60)
            if r.status_code in (200, 204):
                patched += 1
                print(f"  [modrinth] PATCH {m['modrinth_id']} -> {r.status_code} OK")
            else:
                print(f"  [modrinth] PATCH {m['modrinth_id']} -> {r.status_code} ERR {r.text[:200]}")

    print(f"\nDone: {updated_manifests} manifests updated, {patched} Modrinth projects patched.")


if __name__ == "__main__":
    main()
