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

# introspect createPost argument type
q = '''
{
  __type(name: "Mutation") {
    fields {
      name
      args { name type { kind name ofType { kind name ofType { kind name } } } }
    }
  }
}
'''
r = gql(q)
for f in r.get("data", {}).get("__type", {}).get("fields", []):
    if f["name"] == "createPost":
        print("createPost args:")
        for a in f["args"]:
            t = a["type"]
            def tn(x):
                if not x: return ""
                if x.get("name"): return x["name"]
                return tn(x.get("ofType"))
            print("  ", a["name"], ":", tn(t))

print("\n=== input type object names (chercher CreatePostInput) ===")
r2 = gql('{ __schema { types { name kind } } }')
names = [t["name"] for t in r2.get("data", {}).get("__schema", {}).get("types", [])
         if t["kind"] in ("INPUT_OBJECT", "OBJECT") and ("Post" in t["name"] or "Media" in t["name"] or "Asset" in t["name"])]
print(sorted(set(names)))
