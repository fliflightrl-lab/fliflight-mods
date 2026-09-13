#!/usr/bin/env python3
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
        return {"http_error": e.code, "body": e.read().decode()[:2000]}

r = gql('{ __type(name:"PostActionPayload"){ kind name possibleTypes{ name } fields{ name type{ kind name ofType{ kind name } } } } }')
t = r["data"]["__type"]
print("PostActionPayload kind:", t["kind"])
if t.get("possibleTypes"):
    print("members:", [p["name"] for p in t["possibleTypes"]])
for f in (t.get("fields") or []):
    print("  field:", f["name"])
