#!/usr/bin/env python3
"""Pointe le don Ko-fi de tous mes projets Modrinth vers ko-fi.com/fliflight."""
import json, os, urllib.request

creds = json.load(open(os.path.expanduser("~/.config/fliflightmc/credentials.json")))
MT = creds["modrinth"]["token"]
UID = creds["modrinth"].get("user_id", "sG9DNUJw")
API = "https://api.modrinth.com/v2"
HDR = {"Authorization": f"Bearer {MT}", "Content-Type": "application/json",
       "User-Agent": "fliflight/1.0 (fliflight.rl@gmail.com)"}

def req(method, path, body=None):
    r = urllib.request.Request(API + path, method=method, headers=HDR,
                               data=json.dumps(body).encode() if body else None)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        return {"__http": e.code, "__body": e.read().decode()[:400]}

projects = req("GET", f"/user/{UID}/projects")
if isinstance(projects, dict):
    print("erreur liste:", projects); raise SystemExit(1)

print(f"{len(projects)} projets Modrinth\n")
KO = [{"id": "ko-fi", "platform": "Ko-fi", "url": "https://ko-fi.com/fliflight"}]
ok = fail = 0
for p in projects:
    slug = p["slug"]
    old = p.get("donation_urls") or []
    res = req("PATCH", f"/project/{slug}", {"donation_urls": KO})
    if isinstance(res, dict) and res.get("__http"):
        fail += 1
        print(f"  FAIL {slug}: {res['__http']} {res['__body'][:120]}")
    else:
        ok += 1
        oldtxt = ", ".join(u.get("url","") for u in old) or "(aucun)"
        print(f"  OK   {slug:22s} ancien: {oldtxt}")

print(f"\n{ok} mis à jour, {fail} échecs")
