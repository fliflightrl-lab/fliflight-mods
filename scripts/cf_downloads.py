#!/usr/bin/env python3
"""Weekly CurseForge download tracker (stdlib only — urllib). Prints a French delta
report and stores the new baseline in ~/.config/fliflightmc/cf_downloads_baseline.json."""
import json, os, urllib.request

CREDS = os.path.expanduser("~/.config/fliflightmc/credentials.json")
STATE = os.path.expanduser("~/.config/fliflightmc/cf_downloads_baseline.json")

PACKS = [
    (1499007, "Dot Crosshair"),
    (1499029, "CrossX Crosshair"),
    (1494020, "Better Crosshair"),
    (1499072, "Bigger Dot"),
    (1497428, "CrosshairX"),
    (1588694, "Sniper Crosshair"),
    (1558798, "Crossy Crosshair"),
    (1334611, "Visible Ores"),
    (1334714, "Short Sword"),
    (1479652, "Diamond Dimension"),
]


def fetch(key, cid):
    req = urllib.request.Request(f"https://api.curseforge.com/v1/mods/{cid}",
                                 headers={"x-api-key": key})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]["downloadCount"]


def main():
    key = json.load(open(CREDS, encoding="utf-8"))["curseforge"]["api_key"]
    prev = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}

    now = {}
    for cid, label in PACKS:
        now[str(cid)] = {"label": label, "downloads": fetch(key, cid)}
    json.dump(now, open(STATE, "w", encoding="utf-8"), indent=2)

    total = sum(x["downloads"] for x in now.values())
    out = ["📊 **Suivi CurseForge**", ""]
    if prev:
        ptotal = sum(x.get("downloads", 0) for x in prev.values())
        out.append(f"Total : **{total:,}** téléchargements — **{total - ptotal:+,}** cette semaine")
    else:
        out.append(f"Total : **{total:,}** téléchargements (baseline initiale)")
    out.append("")
    out.append("| Pack | Total | Δ semaine |")
    out.append("|---|---|---|")
    for cid, x in sorted(now.items(), key=lambda kv: kv[1]["downloads"], reverse=True):
        pd = prev.get(cid, {}).get("downloads", x["downloads"])
        out.append(f"| {x['label']} | {x['downloads']:,} | {x['downloads'] - pd:+,} |")
    print("\n".join(out))


if __name__ == "__main__":
    main()
