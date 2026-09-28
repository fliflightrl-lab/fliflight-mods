import json

def load(p):
    return json.load(open(p))

live = load("live_raw.json")          # 13 Sep
prev = load("fresh_raw.json")         # 11 Sep
old  = load("../_revenue_report/raw.json")  # 7 Sep

def cf_map(d):
    return {m["id"]: (m["name"], m["downloadCount"], m["classId"]) for m in d["curseforge"]}

def mr_map(d):
    return {p["id"]: (p["title"], p["downloads"], p["project_type"]) for p in d["modrinth"]}

cfL, cfP, cfO = cf_map(live), cf_map(prev), cf_map(old)
mrL, mrP, mrO = mr_map(live), mr_map(prev), mr_map(old)

# short names for CF
short = {
 1588694:"Sniper Crosshair",1558798:"Crossy Crosshair",1655379:"Custom Crosshair PvP (mod)",
 1653138:"Low Fire",1653188:"PvP Essentials",1655357:"PvP HUD (mod)",1653159:"Clear Pumpkin",
 1479652:"Diamond Dimension (mod)",1334714:"Short Sword",1497428:"CrosshairX",1499072:"Bigger Dot",
 1334611:"Visible Ores",1494020:"CrossX Better",1499029:"CrossX CrossX",1499007:"Dot Crosshair",
}
mrshort = {
 "Y8zhQ9z5":"CrosshairX","4JKFVXUw":"Sniper Crosshair","sQkn3uEf":"Crossy Crosshair",
 "IcIJjhMO":"Short Sword","4r8Ufv9p":"Dot Crosshair","NR54mkOD":"Diamond Dimension (mod)",
 "1ylCihJa":"CrossX CrossX","oBGsX8oY":"Better Crosshair","xnQODGjN":"Clear Pumpkin",
 "ruCFBIgj":"PvP HUD (mod)","d8t14H03":"Bigger Dot","o01bugzT":"Custom Crosshair (mod)",
 "RIH3vxZQ":"Low Fire","cHpwGcrb":"PvP Essentials","SEfn6MDy":"Visible Ores",
}

print("="*100)
print("CURSEFORGE  (7 Sep -> 11 Sep -> 13 Sep)")
print("="*100)
print(f"{'Project':28s} {'7Sep':>7s} {'11Sep':>7s} {'13Sep':>7s} {'D7-13':>7s} {'%7-13':>7s}")
rows=[]
for cid,(name,dl,cls) in cfL.items():
    d7 = cfO.get(cid,(name,0,0))[1]
    d11= cfP.get(cid,(name,0,0))[1]
    d13= dl
    rows.append((short.get(cid,name), d7, d11, d13))
for name,d7,d11,d13 in sorted(rows,key=lambda r:-r[3]):
    dd=d13-d7
    pct=(d13/d7*100-100) if d7 else 0
    print(f"{name:28s} {d7:7d} {d11:7d} {d13:7d} {dd:+7d} {pct:+6.1f}%")
t7=sum(r[1] for r in rows); t11=sum(r[2] for r in rows); t13=sum(r[3] for r in rows)
print("-"*100)
print(f"{'TOTAL CurseForge':28s} {t7:7d} {t11:7d} {t13:7d} {t13-t7:+7d} {(t13/t7*100-100):+6.1f}%")

print()
print("="*100)
print("MODRINTH  (7 Sep -> 11 Sep -> 13 Sep)")
print("="*100)
print(f"{'Project':28s} {'7Sep':>7s} {'11Sep':>7s} {'13Sep':>7s} {'D7-13':>7s} {'%7-13':>7s}")
rows=[]
for mid,(title,dl,pt) in mrL.items():
    d7 = mrO.get(mid,(title,0,""))[1]
    d11= mrP.get(mid,(title,0,""))[1]
    d13= dl
    rows.append((mrshort.get(mid,title), d7, d11, d13))
for name,d7,d11,d13 in sorted(rows,key=lambda r:-r[3]):
    dd=d13-d7
    pct=(d13/d7*100-100) if d7 else 0
    print(f"{name:28s} {d7:7d} {d11:7d} {d13:7d} {dd:+7d} {pct:+6.1f}%")
m7=sum(r[1] for r in rows); m11=sum(r[2] for r in rows); m13=sum(r[3] for r in rows)
print("-"*100)
print(f"{'TOTAL Modrinth':28s} {m7:7d} {m11:7d} {m13:7d} {m13-m7:+7d} {(m13/m7*100-100):+6.1f}%")

# github
gh_live = sum(r["downloads"] for r in live["github"]["releases"])
gh_prev = sum(r["downloads"] for r in prev["github"]["releases"])
print()
print("GITHUB releases asset downloads: live", gh_live, "| prev", gh_prev)

print()
print("="*100)
print("GRAND TOTALS (13 Sep)")
print("="*100)
grand13 = t13+m13+gh_live
print(f"CurseForge : {t13:>8d}  ({t13/grand13*100:5.2f}%)")
print(f"Modrinth   : {m13:>8d}  ({m13/grand13*100:5.2f}%)")
print(f"GitHub     : {gh_live:>8d}  ({gh_live/grand13*100:5.2f}%)")
print(f"TOTAL      : {grand13:>8d}")

print()
print("DELTA vs 11 Sep (2 jours): CF", t13-t11, " MR", m13-m11, " GH", gh_live-gh_prev, " TOTAL", (t13-t11)+(m13-m11)+(gh_live-gh_prev))
print("DELTA vs 7 Sep (6 jours):  CF", t13-t7, " MR", m13-m7)
print("Growth rate CF (par jour, 7->13):", round((t13-t7)/6,1), "/jour")
print("Growth rate CF (par jour, 11->13):", round((t13-t11)/2,1), "/jour")
