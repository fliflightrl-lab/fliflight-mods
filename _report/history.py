import json, os

def load(p):
    return json.load(open(p, encoding="utf-8"))

# Historical raw dumps (by date)
hist = {
    "07 Sep": r"C:\Users\user\fliflight-mods\_revenue_report\raw.json",
    "11 Sep": r"C:\Users\user\fliflight-mods\_report\fresh_raw.json",
    "13 Sep": r"C:\Users\user\fliflight-mods\_report\live_raw.json",
}

def cf_total(d):
    if "curseforge" not in d: return 0
    c = d["curseforge"]
    if isinstance(c, list):
        return sum(m.get("downloadCount", 0) for m in c)
    if isinstance(c, dict) and "mods" in c:
        return sum(m.get("downloadCount", 0) for m in c["mods"])
    return 0

def mr_total(d):
    if "modrinth" not in d: return 0
    c = d["modrinth"]
    if isinstance(c, list):
        return sum(p.get("downloads", 0) for p in c)
    if isinstance(c, dict) and "projects" in c:
        return sum(p.get("downloads", 0) for p in c["projects"])
    return 0

def gh_total(d):
    g = d.get("github", {})
    rels = g.get("releases", [])
    return sum(r.get("downloads", 0) for r in rels)

print("Historical series:")
for lbl, p in hist.items():
    try:
        d = load(p)
        print(f"  {lbl}: CF={cf_total(d):,}  MR={mr_total(d):,}  GH={gh_total(d):,}")
    except Exception as e:
        print(f"  {lbl}: ERR {e}")

# fresh (15 Sep)
f = load(r"C:\Users\user\fliflight-mods\_report\fresh_2026_09_15.json")
cf15 = sum(m["downloads"] for m in f["curseforge"])
mr15 = sum(p["downloads"] for p in f["modrinth"])
gh15 = f["github"]["total_downloads"]
print(f"  15 Sep: CF={cf15:,}  MR={mr15:,}  GH={gh15:,}")

# snapshot 14 Sep
snap = load(r"C:\Users\user\.config\fliflightmc\platform_snapshot_2026-09-14.json")
cf14 = snap["curseforge"]["total_downloads"]
mr14 = snap["modrinth"]["total_downloads"]
gh14m = snap["github"]["mod_downloads"]
gh14v = snap["github"]["shorts_video_downloads"]
print(f"  14 Sep: CF={cf14:,}  MR={mr14:,}  GH_mod={gh14m:,}  GH_video={gh14v:,}")

print()
print("Deltas 14->15 Sep:")
print(f"  CF: {cf15-cf14:+,}")
print(f"  MR: {mr15-mr14:+,}")
# github: split mod vs video. 15 sep mods = 111 - 104 = 7 ; video = 104
gh15m = 7; gh15v = 104
print(f"  GH mod: {gh15m-gh14m:+,}   GH video: {gh15v-gh14v:+,}")
