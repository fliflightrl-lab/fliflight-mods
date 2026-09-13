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

def describe(name):
    q = '{ __type(name: "%s") { name kind inputFields { name type { kind name ofType { kind name ofType { kind name } } } } fields { name type { kind name ofType { kind name } } } } }' % name
    r = gql(q)
    t = r.get("data", {}).get("__type")
    if not t:
        print(name, "-> ?", json.dumps(r)[:200]); return
    def tn(x):
        if not x: return ""
        if x.get("name"): return x["name"]
        return tn(x.get("ofType"))
    fields = t.get("inputFields") or t.get("fields") or []
    print(f"\n=== {name} ({t['kind']}) ===")
    for f in fields:
        print(f"  {f['name']}: {tn(f['type'])}")

for n in ["CreatePostInput", "PostInput", "VideoAssetInput", "AssetInput",
          "MediaConfiguration", "YoutubePostMetadataInput", "TikTokPostMetadataInput", "TiktokPostMetadata"]:
    describe(n)
