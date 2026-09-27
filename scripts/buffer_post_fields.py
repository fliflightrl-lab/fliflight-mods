#!/usr/bin/env python3
"""Champs du type Post (chercher un lien vers la vidéo publiée)."""
import json, os, urllib.request

creds = json.load(open(os.path.expanduser("~/.config/fliflightmc/credentials.json")))
b = creds["buffer"]
TOKEN, URL, ORG = b["token"], b["graphql_endpoint"], b["organization_id"]

def gql(q, v=None):
    body = {"query": q}
    if v: body["variables"] = v
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "body": e.read().decode()[:600]}

r = gql('{ __type(name:"Post"){ fields { name type { kind name ofType { kind name } } } } }')
fields = (r.get("data") or {}).get("__type", {}).get("fields", [])
print("=== champs du type Post ===")
for f in fields:
    t = f["type"].get("name") or (f["type"].get("ofType") or {}).get("name")
    print(f"  {f['name']:28s} {f['type']['kind']:10s} {t or ''}")
