#!/usr/bin/env python3
import json, os, urllib.request

creds = json.load(open(os.path.expanduser("~/.config/fliflightmc/credentials.json")))
b = creds["buffer"]
TOKEN, URL, ORG = b["token"], b["graphql_endpoint"], b["organization_id"]

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
        return {"http_error": e.code, "body": e.read().decode()[:1500]}

# essayer avec pagination large
for q, label in [
    ('query($o: OrganizationId!){ posts(input:{ organizationId: $o }, first: 100){ edges { node { dueAt channel { service } status } } } }', "first:100"),
    ('query($o: OrganizationId!){ posts(input:{ organizationId: $o, first: 100 }){ edges { node { dueAt channel { service } status } } } }', "input.first"),
]:
    r = gql(q, {"o": ORG})
    if "data" in r and r.get("data"):
        edges = r["data"]["posts"]["edges"]
        from collections import Counter
        c = Counter(e["node"]["channel"]["service"] for e in edges)
        print(f"[{label}] total={len(edges)} par chaîne={dict(c)}")
        for e in sorted(edges, key=lambda x: x["node"]["dueAt"]):
            print("   ", e["node"]["dueAt"], e["node"]["channel"]["service"], e["node"]["status"])
        break
    else:
        print(f"[{label}] erreur:", json.dumps(r, ensure_ascii=False)[:300])
