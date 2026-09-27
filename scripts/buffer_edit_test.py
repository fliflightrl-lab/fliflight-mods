#!/usr/bin/env python3
"""Test: peut-on éditer le texte d'un post Buffer déjà publié (statut sent) ?"""
import json, os, urllib.request

creds = json.load(open(os.path.expanduser("~/.config/fliflightmc/credentials.json")))
b = creds["buffer"]
TOKEN, URL = b["token"], b["graphql_endpoint"]

MUT = """mutation EditPost($input: EditPostInput!) {
  editPost(input: $input) {
    __typename
    ... on PostActionSuccess { post { id text dueAt status } }
    ... on InvalidInputError { message }
    ... on UnexpectedError { message }
    ... on RestProxyError { message }
    ... on NotFoundError { message }
    ... on UnauthorizedError { message }
    ... on LimitReachedError { message }
  }
}"""

def gql(q, v=None):
    body = {"query": q}
    if v: body["variables"] = v
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "body": e.read().decode()[:800]}

# récupérer le texte d'un post envoyé (le 1er TikTok du 14/09)
PID = "6aa725fa66679b076f362e7d"
q = """query($o: OrganizationId!){ posts(input:{ organizationId: $o }, first: 100){
  edges { node { id text status dueAt } } } }"""
r = gql(q, {"o": b["organization_id"]})
node = next((e["node"] for e in r["data"]["posts"]["edges"] if e["node"]["id"] == PID), None)
print("=== post cible ===")
print(" id    :", PID)
print(" statut:", node["status"] if node else "?")
print(" texte :", (node["text"][:160] + "...") if node and node.get("text") else "(vide)")

if node:
    old = node.get("text") or ""
    new = old.rstrip() + "\n\n☕ Soutiens-moi : https://ko-fi.com/fliflight"
    res = gql(MUT, {"input": {"id": PID, "text": new}}).get("data", {}).get("editPost", {})
    tn = res.get("__typename")
    print("\n=== resultat editPost ===")
    print(" ", tn, "-", res.get("message") or "")
    if tn == "PostActionSuccess":
        print("  nouveau texte:", res["post"]["text"][:200].replace("\n", " | "))
