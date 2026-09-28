import json
d = json.load(open("raw.json"))
cf = d["curseforge"]; mr = d["modrinth"]
cf_total = sum(m["downloadCount"] for m in cf)
mr_total = sum(p["downloads"] for p in mr)
total = cf_total + mr_total
print("CF", len(cf), cf_total)
print("MR", len(mr), mr_total)
print("TOTAL", total)
print("CF%", round(100*cf_total/total,2))
print("MR%", round(100*mr_total/total,2))
print("RATIO", round(cf_total/mr_total,1))
cf_rp = sum(m["downloadCount"] for m in cf if m["classId"]==12)
cf_mod = sum(m["downloadCount"] for m in cf if m["classId"]==6)
mr_rp = sum(p["downloads"] for p in mr if p["project_type"]=="resourcepack")
mr_mod = sum(p["downloads"] for p in mr if p["project_type"]=="mod")
print("CFrp", cf_rp, "CFmod", cf_mod)
print("MRrp", mr_rp, "MRmod", mr_mod)
