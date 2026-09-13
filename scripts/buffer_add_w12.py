#!/usr/bin/env python3
"""Ajoute w12 sur Buffer si absent (idempotent). Sûr à relancer quotidiennement."""
import json, os, urllib.request

creds = json.load(open(os.path.expanduser("~/.config/fliflightmc/credentials.json")))
b = creds["buffer"]
TOKEN, URL, ORG = b["token"], b["graphql_endpoint"], b["organization_id"]
YT = "6a7f5d27b2d9d5774379e036"
TT = "6a7f6079b2d9d577437a0f78"
DUE = "2026-09-23T18:00:00+02:00"
DUE_UTC_PREFIX = "2026-09-23"

MUT = """mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    __typename
    ... on PostActionSuccess { post { id dueAt } }
    ... on LimitReachedError { message }
    ... on InvalidInputError { message }
    ... on UnexpectedError { message }
    ... on RestProxyError { message }
    ... on NotFoundError { message }
    ... on UnauthorizedError { message }
  }
}"""

def gql(query, variables=None):
    body = {"query": query}
    if variables: body["variables"] = variables
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {TOKEN}",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "body": e.read().decode()[:800]}

# quels canaux ont déjà un post le 23/09 ?
r = gql('query($o: OrganizationId!){ posts(input:{ organizationId: $o }, first: 100){ edges { node { dueAt status channel { service } } } } }', {"o": ORG})
existing = set()
try:
    for e in r["data"]["posts"]["edges"]:
        n = e["node"]
        if str(n.get("dueAt","")).startswith(DUE_UTC_PREFIX):
            existing.add(n["channel"]["service"])
except Exception:
    pass

VID = "https://github.com/fliflightrl-lab/fliflight-mods/releases/download/shorts-pvp-batch1/final_w12.mp4"
TITLE = "ET BOOM. 💥 (Minecraft PvP)"
DESC = ("🔥 ET BOOM. — clutch Minecraft PvP !\n\n"
        "⚔️ Crosshair custom, ores visibles, épées courtes… tous mes packs sont GRATUITS "
        "👉 https://linktr.ee/fliflight\n"
        "💬 Discord, réseaux & tout le reste : même lien en bio\n\n"
        "Abonne-toi pour plus de PvP 🔥\n\n"
        "#minecraft #minecraftpvp #pvp #shorts #gaming #crosshair #fyp")

out = []
acted = False
for ch, name, svc in [(YT, "YouTube", "youtube"), (TT, "TikTok", "tiktok")]:
    if svc in existing:
        continue  # déjà programmé -> silencieux
    acted = True
    inp = {"channelId": ch, "text": DESC,
           "assets": [{"video": {"url": VID, "metadata": {"title": TITLE}}}],
           "mode": "customScheduled", "schedulingType": "automatic",
           "needsApproval": False, "dueAt": DUE}
    if ch == YT:
        inp["metadata"] = {"youtube": {"title": TITLE, "privacy": "public", "madeForKids": False,
                                       "categoryId": "20", "notifySubscribers": True, "isAiGenerated": False}}
    else:
        inp["metadata"] = {"tiktok": {"title": TITLE, "isAiGenerated": False}}
    res = gql(MUT, {"input": inp}).get("data", {}).get("createPost", {})
    if res.get("__typename") == "PostActionSuccess":
        out.append(f"✅ {name}: w12 « ET BOOM. » programmé pour le 23/09 18h (id {res['post']['id']})")
    else:
        out.append(f"❌ {name}: {res.get('__typename')} — {res.get('message','')}")

# silencieux si rien n'était à faire (déjà programmé)
if acted:
    print("Buffer — ajout du dernier short (w12)")
    print("\n".join(out))
