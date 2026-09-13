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
        return {"http_error": e.code, "body": e.read().decode()[:2000]}

for name in ["PostActionSuccess", "InvalidInputError", "LimitReachedError", "UnexpectedError", "RestProxyError", "NotFoundError", "UnauthorizedError"]:
    r = gql('{ __type(name:"%s"){ fields{ name } } }' % name)
    t = r.get("data", {}).get("__type")
    print(name, "->", [f["name"] for f in t["fields"]] if t else r)
