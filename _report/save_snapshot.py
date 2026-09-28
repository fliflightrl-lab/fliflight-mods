import json
f = json.load(open(r"C:\Users\user\fliflight-mods\_report\fresh_2026_09_15.json", encoding="utf-8"))
snap = {
    "date": "2026-09-15",
    "curseforge": {
        "total_downloads": sum(m["downloads"] for m in f["curseforge"]),
        "projects": len(f["curseforge"]),
        "mods": [{"id": m["id"], "name": m["name"], "dl": m["downloads"]} for m in f["curseforge"]],
    },
    "modrinth": {
        "total_downloads": sum(p["downloads"] for p in f["modrinth"]),
        "projects": len(f["modrinth"]),
    },
    "github": {
        "mod_downloads": 7,
        "shorts_video_downloads": f["github"]["total_downloads"] - 7,
    },
    "grand_total_mods": sum(m["downloads"] for m in f["curseforge"]) + sum(p["downloads"] for p in f["modrinth"]) + 7,
}
json.dump(snap, open(r"C:\Users\user\.config\fliflightmc\platform_snapshot_2026-09-15.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("saved platform_snapshot_2026-09-15.json")
print("grand_total_mods:", snap["grand_total_mods"])
