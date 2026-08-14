#!/usr/bin/env python3
"""
One-time migration: turn the existing ~/curseforge-to-modrinth mirror artifacts
(plan.json + downloads/) into a clean source-of-truth repo layout:

    packs/<slug>/
        manifest.json      # canonical metadata
        files/<file>       # the release artifact (zip/jar)
        icon.<ext>
        gallery/<i>.<ext>

Reads plan.json and downloads/ from ~/curseforge-to-modrinth by default.
Override with PLAN_JSON and DOWNLOADS_DIR env vars.
"""
import json, os, shutil, sys

BASE = os.path.expanduser("~/curseforge-to-modrinth")
PLAN_JSON = os.environ.get("PLAN_JSON", os.path.join(BASE, "plan.json"))
DOWNLOADS = os.environ.get("DOWNLOADS_DIR", os.path.join(BASE, "downloads"))
OUT = os.environ.get("OUT_DIR", os.path.expanduser("~/fliflight-mods"))
PACKS = os.path.join(OUT, "packs")

# cf_id -> (modrinth_id, modrinth_slug)  — verified against the live Modrinth API.
CF_TO_MR = {
    1334611: ("SEfn6MDy", "visible-ores-all-versions-and-netherite"),
    1588694: ("4JKFVXUw", "crossx"),
    1497428: ("Y8zhQ9z5", "crosshairx-better-crosshair"),
    1494020: ("oBGsX8oY", "crossx-better-crosshair"),
    1499007: ("4r8Ufv9p", "dot-crosshair-cossx-better-crosshair"),
    1558798: ("sQkn3uEf", "crossy-crossx-better-crosshair"),
    1499029: ("1ylCihJa", "crossx-crossx-better-crosshair"),
    1479652: ("NR54mkOD", "all-in-diamonds-dimension"),
    1334714: ("IcIJjhMO", "pvp-sword-little-sword-all-versions"),
    1499072: ("d8t14H03", "bigger-dot-crosshair-cossx-better-crosshair"),
}


def ext_of(path):
    e = os.path.splitext(path)[1].lstrip(".").lower()
    return e if e else "png"


def main():
    plan = json.load(open(PLAN_JSON, encoding="utf-8"))
    os.makedirs(PACKS, exist_ok=True)
    n = 0
    for e in plan:
        cf_id = e["cf_id"]
        if cf_id not in CF_TO_MR:
            print(f"SKIP cf_id={cf_id} (no Modrinth id in map) — {e['title']}")
            continue
        mr_id, slug = CF_TO_MR[cf_id]
        pdir = os.path.join(PACKS, slug)
        os.makedirs(os.path.join(pdir, "files"), exist_ok=True)
        os.makedirs(os.path.join(pdir, "gallery"), exist_ok=True)

        # copy release artifact
        v = e["version"]
        src = v["file_path"]
        dst_file = os.path.join(pdir, "files", v["file_name"])
        if os.path.exists(src):
            shutil.copy(src, dst_file)
        else:
            print(f"WARN missing file {src}")

        # copy icon
        icon_src = e.get("icon_path")
        icon_name = None
        if icon_src and os.path.exists(icon_src):
            icon_name = f"icon.{ext_of(icon_src)}"
            shutil.copy(icon_src, os.path.join(pdir, icon_name))

        # copy gallery
        gallery = []
        for i, gp in enumerate(e.get("gallery_paths", [])):
            if os.path.exists(gp):
                gname = f"gallery_{i}.{ext_of(gp)}"
                shutil.copy(gp, os.path.join(pdir, "gallery", gname))
                gallery.append(gname)

        manifest = {
            "slug": slug,
            "name": e["title"],
            "project_type": e["project_type"],  # resourcepack | mod
            "summary": e["summary"],
            "body": e["body"],
            "license": "All Rights Reserved",
            "categories": e["categories"],
            "curseforge_id": cf_id,
            "modrinth_id": mr_id,
            "client_side": e.get("client_side"),
            "server_side": e.get("server_side"),
            "links": e.get("links", {}),
            "version": {
                "number": v["version_number"],
                "type": v["version_type"],
                "changelog": v.get("changelog", ""),
                "loaders": v["loaders"],
                "game_versions": v["game_versions"],
            },
            "file": v["file_name"],
            "icon": icon_name,
            "gallery": gallery,
        }
        mp = os.path.join(pdir, "manifest.json")
        json.dump(manifest, open(mp, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print(f"OK  {slug:48} cf={cf_id} mr={mr_id} type={e['project_type']}")
        n += 1
    print(f"\nGenerated {n} packs under {PACKS}")


if __name__ == "__main__":
    sys.exit(main())
