#!/usr/bin/env python3
import json, os, urllib.request

creds = json.load(open(os.path.expanduser("~/.config/fliflightmc/credentials.json")))
b = creds["buffer"]
TOKEN, URL, ORG = b["token"], b["graphql_endpoint"], b["organization_id"]
YT = "6a7f5d27b2d9d5774379e036"
TT = "6a7f6079b2d9d577437a0f78"

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
        return {"http_error": e.code, "body": e.read().decode()[:1200]}

# compter les posts programmés
q = 'query($o: OrganizationId!){ posts(input:{ organizationId: $o }){ edges { node { id dueAt status channel { service } } } } }'
r = gql(q, {"o": ORG})
if "data" in r and r.get("data"):
    posts = r["data"]["posts"]["edges"]
    print(f"total posts: {len(posts)}")
    for p in posts:
        n = p["node"]
        print(f"  {n['channel']['service']:8s} {n.get('dueAt')} {n.get('status')}")
else:
    print("posts query:", json.dumps(r, ensure_ascii=False)[:800])

# plan / limites
r2 = gql('{ account { email preferences { __typename } } }')
print("\naccount prefs:", json.dumps(r2, ensure_ascii=False)[:400])
