#!/usr/bin/env python3
"""Finish Modrinth publishing: submit for review + icon + gallery (project already created)."""
import json, os
import requests

BASE = r"C:\Users\user\fliflight-mods"
PK   = os.path.join(BASE, "packs", "pvp-essentials")
CRED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))
TOKEN = CRED["modrinth"]["token"]
HDR   = {"Authorization": TOKEN}
API   = "https://api.modrinth.com/v2"
PID   = "cHpwGcrb"  # already created
m = json.load(open(os.path.join(PK, "manifest.json")))

def show(r, label):
    body = r.text.strip()
    print(f"{label}: {r.status_code} {body[:200] if body else '(empty)'}")

# current state
r = requests.get(f"{API}/project/{PID}", headers=HDR)
if r.ok:
    p = r.json()
    print(f"current: status={p.get('status')} project_type={p.get('project_type')} versions={len(p.get('versions', []))}")

# submit for review
r = requests.patch(f"{API}/project/{PID}", headers=HDR, json={"status": "processing"})
show(r, "submit review")

# icon
with open(os.path.join(PK, m["icon"]), "rb") as f:
    r = requests.patch(f"{API}/project/{PID}/icon?ext=png", headers={**HDR, "Content-Type": "image/png"}, data=f.read())
show(r, "icon")

# gallery
with open(os.path.join(PK, "gallery", m["gallery"][0]), "rb") as f:
    r = requests.post(f"{API}/project/{PID}/gallery?ext=png&featured=false&ordering=0",
                      headers={**HDR, "Content-Type": "image/png"}, data=f.read())
show(r, "gallery")

# final state
r = requests.get(f"{API}/project/{PID}", headers=HDR)
if r.ok:
    p = r.json()
    print(f"\nFINAL: status={p.get('status')} type={p.get('project_type')} icon_url={bool(p.get('icon_url'))} gallery={len(p.get('gallery', []))} versions={len(p.get('versions', []))}")
    print(f"URL: https://modrinth.com/resourcepack/{p.get('slug')}")
