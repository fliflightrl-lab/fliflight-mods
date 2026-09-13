#!/usr/bin/env python3
"""Test: peut-on ajouter w12 via addToQueue malgré la limite ?"""
import json, os, urllib.request

creds = json.load(open(os.path.expanduser("~/.config/fliflightmc/credentials.json")))
b = creds["buffer"]
TOKEN, URL = b["token"], b["graphql_endpoint"]
YT = "6a7f5d27b2d9d5774379e036"
TT = "6a7f6079b2d9d577437a0f78"

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
        return {"http_error": e.code, "body": e.read().decode()[:1200]}

VID = "https://github.com/fliflightrl-lab/fliflight-mods/releases/download/shorts-pvp-batch1/final_w12.mp4"
TITLE = "ET BOOM. 💥 (Minecraft PvP)"
DESC = ("🔥 ET BOOM. — clutch Minecraft PvP !\n\n"
        "⚔️ Crosshair custom, ores visibles, épées courtes… tous mes packs sont GRATUITS "
        "👉 https://linktr.ee/fliflight\n"
        "💬 Discord, réseaux & tout le reste : même lien en bio\n\n"
        "Abonne-toi pour plus de PvP 🔥\n\n"
        "#minecraft #minecraftpvp #pvp #shorts #gaming #crosshair #fyp")

inp = {
    "channelId": YT,
    "text": DESC,
    "assets": [{"video": {"url": VID, "metadata": {"title": TITLE}}}],
    "metadata": {"youtube": {"title": TITLE, "privacy": "public", "madeForKids": False,
                             "categoryId": "20", "notifySubscribers": True, "isAiGenerated": False}},
    "mode": "addToQueue",
    "schedulingType": "automatic",
    "needsApproval": False,
}
r = gql(MUT, {"input": inp})
print("addToQueue w12 YT:", json.dumps(r.get("data", r), ensure_ascii=False)[:400])
