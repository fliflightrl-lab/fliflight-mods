import json

f = json.load(open(r"C:\Users\user\fliflight-mods\_report\fresh_2026_09_15.json", encoding="utf-8"))
snap = json.load(open(r"C:\Users\user\.config\fliflightmc\platform_snapshot_2026-09-14.json", encoding="utf-8"))

# --- CF per-project deltas vs 14 Sep ---
cf14_map = {m["id"]: m["dl"] for m in snap["curseforge"]["mods"]}
cf_rows = []
for m in f["curseforge"]:
    dl = m["downloads"]
    prev = cf14_map.get(m["id"], dl)
    cf_rows.append((m["name"], dl, prev, dl - prev))
cf_total = sum(r[1] for r in cf_rows)
cf_delta = sum(r[3] for r in cf_rows)

# --- MR ---
mr_rows = [(p["title"], p["downloads"], p["status"]) for p in f["modrinth"]]
mr_total = sum(r[1] for r in mr_rows)
mr_prev = snap["modrinth"]["total_downloads"]

# --- GH ---
gh_total = f["github"]["total_downloads"]  # 111
gh_mod = 7
gh_video = gh_total - gh_mod

grand_mods = cf_total + mr_total + gh_mod
grand_all = cf_total + mr_total + gh_total

def pct(a, b): return a/b*100 if b else 0

print("TOTAL MOD DOWNLOADS:", grand_mods)
print()
# platform table
print("PLATFORM | downloads | share% | delta(14->15)")
print(f"CurseForge | {cf_total:,} | {pct(cf_total,grand_mods):.2f}% | +{cf_delta:,}")
print(f"Modrinth   | {mr_total:,} | {pct(mr_total,grand_mods):.2f}% | +{mr_total-mr_prev:,}")
print(f"GitHub mods| {gh_mod:,} | {pct(gh_mod,grand_mods):.3f}% | +0")
print(f"(GitHub shorts videos, hors mods) | {gh_video:,}")
print()
print("=== CF per-project (15 Sep) ===")
for name, dl, prev, delta in sorted(cf_rows, key=lambda r:-r[1]):
    print(f"{name[:42]:44s} {dl:>7,}  +{delta:>5,}  ({pct(dl,cf_total):.2f}%)")
print()
print("=== MR per-project (15 Sep) ===")
for title, dl, st in sorted(mr_rows, key=lambda r:-r[1]):
    print(f"{title[:46]:48s} {dl:>6,}  ({pct(dl,mr_total):.2f}%)  [{st}]")
