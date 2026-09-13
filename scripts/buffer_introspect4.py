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
        return {"http_error": e.code, "body": e.read().decode()[:1500]}

def tstr(t):
    if not t: return ""
    if t.get("kind") == "NON_NULL": return tstr(t.get("ofType")) + "!"
    if t.get("kind") == "LIST": return "[" + tstr(t.get("ofType")) + "]"
    return t.get("name") or "?"

# full CreatePostInput with deep resolution
q = '''{ __type(name:"CreatePostInput"){ inputFields{ name type{ kind name ofType{ kind name ofType{ kind name ofType{ kind name }}}}}}}'''
r = gql(q)
print("=== CreatePostInput (complet) ===")
for f in r["data"]["__type"]["inputFields"]:
    print("  ", f["name"], ":", tstr(f["type"]))

# createPost return type
q2 = '''{ __type(name:"Mutation"){ fields{ name type{ kind name ofType{ kind name }}}}}'''
r2 = gql(q2)
for f in r2["data"]["__type"]["fields"]:
    if f["name"] == "createPost":
        print("\ncreatePost returns:", tstr(f["type"]))

for e in ["YoutubePrivacy", "YoutubeLicense"]:
    r3 = gql('{ __type(name:"%s"){ enumValues{ name } } }' % e)
    ev = r3.get("data", {}).get("__type")
    print(f"\n{e}:", [v["name"] for v in ev["enumValues"]] if ev else r3)
