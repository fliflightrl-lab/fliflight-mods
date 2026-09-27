#!/usr/bin/env python3
"""Introspection de editPost + listing des posts programmés."""
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
        return {"http_error": e.code, "body": e.read().decode()[:800]}

# --- signature de editPost ---
q = """
{ __schema { mutationType { fields { name
  args { name type { kind name ofType { kind name ofType { kind name } } } }
  type { kind name ofType { kind name } } } } } }
"""
r = gql(q)
for f in r["data"]["__schema"]["mutationType"]["fields"]:
    if f["name"] == "editPost":
        print("editPost args:", json.dumps(f["args"], indent=1))
        print("editPost returns:", f["type"])

# --- le type d'input ---
q2 = """
{ __type(name:"EditPostInput"){ name inputFields{ name
  type{ kind name ofType{ kind name ofType{ kind name } } } } } }
"""
r2 = gql(q2)
t = (r2.get("data") or {}).get("__type")
print("\nEditPostInput:", json.dumps(t, indent=1) if t else "introuvable")

# --- posts programmés ---
q3 = """
query($o: OrganizationId!){
  posts(input:{ organizationId: $o }, first: 100){
    edges { node { id dueAt text status channel { service } } }
  }
}
"""
r3 = gql(q3, {"o": ORG})
edges = (r3.get("data") or {}).get("posts", {}).get("edges", [])
print(f"\n=== {len(edges)} posts ===")
for e in sorted(edges, key=lambda x: x["node"]["dueAt"]):
    n = e["node"]
    has_kofi = "ko-fi" in (n.get("text") or "").lower()
    print(f"  {n['dueAt'][:16]} {n['channel']['service']:8s} {n['status']:9s} "
          f"kofi={'OUI' if has_kofi else 'non'}  id={n['id']}")
