import json

cf = json.load(open("cf_raw.json", encoding="utf-8"))
mr = json.load(open("mr_raw.json", encoding="utf-8"))

# CF mods by author
cf_mods = [m for m in cf["data"] if any(a.get("name")=="Fliflightmc" for a in m.get("authors",[]))]

# print available keys on one CF mod to check for extra stats
print("CF MOD KEYS:", sorted(cf_mods[0].keys()))
print()

# Build id -> data
cf_by_id = {str(m["id"]): m for m in cf_mods}

# mapping: manifest slug -> (cf_id, mr_id)  (15 projects)
mapping = [
    ("Dot Crosshair", 1499007, "4r8Ufv9p"),
    ("CrossX Crosshair", 1499029, "1ylCihJa"),
    ("Visible Ores", 1334611, "SEfn6MDy"),
    ("Better Crosshair", 1494020, "oBGsX8oY"),
    ("Bigger Dot Crosshair", 1499072, "d8t14H03"),
    ("Short Sword", 1334714, "IcIJjhMO"),
    ("CrosshairX", 1497428, "Y8zhQ9z5"),
    ("Sniper Crosshair", 1588694, "4JKFVXUw"),
    ("Low Fire", 1653138, "RIH3vxZQ"),
    ("Crossy Crosshair", 1558798, "sQkn3uEf"),
    ("Clear Pumpkin", 1653159, "xnQODGjN"),
    ("Diamond Dimension", 1479652, "NR54mkOD"),
    ("PvP Essentials", 1653188, "cHpwGcrb"),
    ("PvP HUD", 1655357, "ruCFBIgj"),
    ("Custom Crosshair", 1655379, "o01bugzT"),
]

mr_by_id = {p["id"]: p for p in mr}

rows = []
cf_total = 0
mr_total = 0
for name, cfid, mrid in mapping:
    c = cf_by_id.get(str(cfid))
    m = mr_by_id.get(mrid)
    cfdl = c["downloadCount"] if c else 0
    mrdl = m["downloads"] if m else 0
    cf_total += cfdl
    mr_total += mrdl
    rows.append((name, cfdl, mrdl))

print(f"{'Project':<24} {'CurseForge':>10} {'Modrinth':>9} {'Total':>7} {'CF%':>6}")
for name, cfdl, mrdl in sorted(rows, key=lambda r: -(r[1]+r[2])):
    tot = cfdl+mrdl
    pct = (cfdl/tot*100) if tot else 0
    print(f"{name:<24} {cfdl:>10,} {mrdl:>9,} {tot:>7,} {pct:>5.1f}%")

print("-"*60)
print(f"{'TOTAL':<24} {cf_total:>10,} {mr_total:>9,} {cf_total+mr_total:>7,} {cf_total/(cf_total+mr_total)*100:>5.1f}%")
print()
print("CF total:", cf_total)
print("MR total:", mr_total)
print("Grand total:", cf_total+mr_total)
print("CF share:", round(cf_total/(cf_total+mr_total)*100, 2), "%")
print("MR share:", round(mr_total/(cf_total+mr_total)*100, 2), "%")
