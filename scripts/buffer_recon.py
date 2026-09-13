#!/usr/bin/env python3
import json, os, urllib.request

creds = json.load(open(os.path.expanduser("~/.config/fliflightmc/credentials.json")))
b = creds["buffer"]
TOKEN = b["token"]
URL = b["graphql_endpoint"]
ORG = b["organization_id"]

def gql(query):
    req = urllib.request.Request(URL, data=json.dumps({"query": query}).encode(),
                                 headers={"Authorization": f"Bearer {TOKEN}",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "body": e.read().decode()[:500]}

print("=== whoami ===")
print(json.dumps(gql("{ account { id email name timezone } }"), ensure_ascii=False)[:400])

print("\n=== channels ===")
print(json.dumps(gql('{ channels(input: { organizationId: "%s" }) { id service name displayName isDisconnected } }' % ORG),
                 ensure_ascii=False)[:800])

print("\n=== Mutation fields (publication dispo ?) ===")
r = gql('{ __type(name: "Mutation") { fields { name } } }')
if "data" in r and r["data"]:
    names = [f["name"] for f in r["data"]["__type"]["fields"]]
    print("mutations:", names)
else:
    print(json.dumps(r, ensure_ascii=False)[:600])
