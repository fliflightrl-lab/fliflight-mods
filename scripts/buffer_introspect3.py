#!/usr/bin/env python3
import json, os, urllib.request

creds = json.load(open(os.path.expanduser("~/.config/fliflightmc/credentials.json")))
b = creds["buffer"]
TOKEN, URL = b["token"], b["graphql_endpoint"]

def gql(query):
    req = urllib.request.Request(URL, data=json.dumps({"query": query}).encode(),
                                 headers={"Authorization": f"Bearer {TOKEN}",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "body": e.read().decode()[:800]}

def tn(x):
    if not x: return ""
    if x.get("name"): return x["name"]
    return tn(x.get("ofType"))

def show(name):
    q = '{ __type(name: "%s") { name kind enumValues { name } inputFields { name type { kind name ofType { kind name ofType { kind name } } } } } }' % name
    r = gql(q); t = r.get("data", {}).get("__type")
    if not t:
        print(name, "-> ?", json.dumps(r)[:200]); return
    print(f"\n=== {name} ({t['kind']}) ===")
    if t.get("enumValues"):
        print("  values:", [v["name"] for v in t["enumValues"]])
    for f in (t.get("inputFields") or []):
        print(f"  {f['name']}: {tn(f['type'])}")

for n in ["ShareMode", "SchedulingType", "PostInputMetaData", "VideoMetadataInput"]:
    show(n)
