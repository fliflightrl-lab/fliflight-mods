#!/usr/bin/env python3
"""Que peut réellement Buffer ? services supportés + mutations liées aux profils/bios."""
import json, os, urllib.request

creds = json.load(open(os.path.expanduser("~/.config/fliflightmc/credentials.json")))
b = creds["buffer"]
TOKEN, URL = b["token"], b["graphql_endpoint"]

def gql(query, variables=None):
    body = {"query": query}
    if variables: body["variables"] = variables
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {TOKEN}",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "body": e.read().decode()[:600]}

# 1) tous les types d'enum contenant "Service" / "Channel" / "Network"
r = gql('{ __schema { types { name kind } } }')
types = r.get("data", {}).get("__schema", {}).get("types", [])
cands = [t["name"] for t in types if t["kind"] == "ENUM"
         and any(k in t["name"].lower() for k in ("service", "channel", "network", "platform"))]
print("=== enums candidats ===")
for c in cands:
    print("  ", c)

# 2) valeurs des enums de service
for name in cands:
    rr = gql('query($n:String!){ __type(name:$n){ name enumValues{ name } } }', {"n": name})
    ev = (rr.get("data", {}).get("__type") or {}).get("enumValues")
    if ev:
        vals = [v["name"] for v in ev]
        print(f"\n=== {name} ({len(vals)}) ===")
        print("  ", ", ".join(vals))

# 3) mutations disponibles
rm = gql('{ __schema { mutationType { fields { name description } } } }')
fields = rm.get("data", {}).get("__schema", {}).get("mutationType", {}).get("fields", [])
print(f"\n=== mutations ({len(fields)}) ===")
for f in fields:
    print(f"  {f['name']}")
