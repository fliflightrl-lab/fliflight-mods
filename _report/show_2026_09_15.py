import json
d = json.load(open(r"C:\Users\user\fliflight-mods\_report\fresh_2026_09_15.json", encoding="utf-8"))
print("FETCHED AT:", d["fetched_at"])
print()
print("=== CURSEFORGE (%d mods) ===" % len(d["curseforge"]))
cf_total = 0
for m in d["curseforge"]:
    cf_total += m["downloads"]
    typ = "mod" if m["classId"] == 6 else "RP" if m["classId"] == 12 else str(m["classId"])
    print("  %9d  %3s  %8d  %s" % (m["id"], typ, m["downloads"], m["name"]))
print("  CF TOTAL: %d" % cf_total)
print()
print("=== MODRINTH (%d projects) ===" % len(d["modrinth"]))
mr_total = 0
for p in d["modrinth"]:
    mr_total += p["downloads"]
    print("  %9s  %-13s  %7d  fw=%3d  %-10s  %s" % (p["id"], p["project_type"], p["downloads"], p["followers"], p["status"], p["title"]))
print("  MR TOTAL: %d" % mr_total)
print()
print("=== MODRINTH USER ===")
print("  payout_data:", d["modrinth_user"]["payout_data"])
print()
print("=== GITHUB ===")
print("  repo:", d["github"]["repo"])
print("  total release downloads:", d["github"]["total_downloads"])
print("  releases dl>0:", [(r["tag"], r["downloads"]) for r in d["github"]["releases"] if r["downloads"] > 0])
print()
print("GRAND TOTAL (CF+MR+GH):", cf_total + mr_total + d["github"]["total_downloads"])
