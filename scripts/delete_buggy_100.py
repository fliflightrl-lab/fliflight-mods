#!/usr/bin/env python3
"""Delete the buggy Modrinth 1.0.0 version (id jZZnruSG)."""
import json, requests
CRED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))
HDR = {"Authorization": CRED["modrinth"]["token"]}
r = requests.delete("https://api.modrinth.com/v2/version/jZZnruSG", headers=HDR)
print(f"delete 1.0.0: {r.status_code} {r.text[:200] if r.text else '(empty)'}")
p = requests.get("https://api.modrinth.com/v2/project/cHpwGcrb", headers=HDR).json()
print(f"project versions now: {len(p.get('versions', []))}")
for vid in p.get("versions", []):
    vv = requests.get(f"https://api.modrinth.com/v2/version/{vid}", headers=HDR).json()
    print(f"  v{vv.get('version_number')}")
