#!/usr/bin/env python3
"""Give every gallery image a title/description, upload the new 2nd image, set featured.

Fixes the Modrinth 'Insufficient Gallery Images (2.1)' rejection:
  - images must have titles that accurately label them
  - a featured image must be set
  - the gallery must show off the content
"""
import json, os, time
import requests

BASE = r"C:\Users\user\fliflight-mods"
PACKS = os.path.join(BASE, "packs")
CRED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))
HDR = {"Authorization": CRED["modrinth"]["token"], "User-Agent": "fliflightmc/1.0"}
API = "https://api.modrinth.com/v2"

# project id -> (slug, [titles in gallery order], extra image file + its title/desc)
PLAN = {
    "fliflight-low-shield": ("3kHplXd9", [
        ("Vanilla vs Low Shield", "Left: the vanilla shield covering your view. Right: this pack - smaller and lower."),
        ("In a fight - the shield stays low", "Holding the shield in combat: your target stays visible."),
    ]),
    "fliflight-no-vignette": ("JYyEzln5", [
        ("Vanilla vs No Vignette", "Left: dark screen corners. Right: this pack - evenly lit, clear view."),
        ("In a deep cave at night", "No corner shading, so the whole screen stays readable in the dark."),
    ]),
    "fliflight-clear-water": ("4KyMcPC1", [
        ("Vanilla vs Clear Water", "Left: opaque water. Right: this pack - the seabed stays visible."),
        ("Underwater - see the terrain", "Swim with a clear view of the ground, ore and mineshafts."),
    ]),
    "fliflight-clear-lava": ("eG9N5405", [
        ("Vanilla vs Clear Lava", "Left: solid lava. Right: this pack - see what is underneath."),
        ("In the Nether - spot the terrain", "Semi-transparent lava, so you can see before you cross."),
    ]),
    "fliflight-clear-spyglass": ("HEAEl6k5", [
        ("Vanilla vs Clear Spyglass", "Left: the black scope overlay. Right: this pack - full clear view."),
        ("Zoomed in - full clear view", "The whole screen stays usable while scoping, spot players from far away."),
    ]),
    "fliflight-clean-hotbar": ("PDnvunp5", [
        ("Vanilla vs Clean Hotbar", "Left: the vanilla hotbar. Right: this pack - flat and minimal, same 9 slots."),
        ("In game with items", "Same 9 slots, far less visual noise while you play."),
    ]),
    "fliflight-thin-totem": ("32hlofGi", [
        ("Vanilla vs Thin Totem", "Left: the vanilla totem. Right: this pack - slimmer, blocks less of the screen."),
        ("Popping a totem mid-fight", "The slimmer totem leaves your view clear when it pops."),
    ]),
    "fliflight-clear-powder-snow": ("fQlGVRS8", [
        ("Vanilla vs Clear Powder Snow", "Left: the frost overlay. Right: this pack - clear vision while freezing."),
        ("Freezing at night", "No frost veil - you can still see the way out."),
    ]),
    "fliflight-clear-pumpkin": ("xnQODGjN", [
        ("Vanilla vs Clear Pumpkin", "Left: the orange pumpkin blur. Right: this pack - the blur is removed."),
        ("Wearing a pumpkin at night", "No orange veil, so mobs and terrain stay visible."),
    ]),
    # the flagship: 9 existing images, titles only + featured
    "fliflight-pvp-essentials": ("cHpwGcrb", [
        ("Dot crosshair", "The clean 1px dot crosshair - nothing blocking your view."),
        ("Crosshair in action", "The dot crosshair during PvP combat."),
        ("Visible ores", "Every ore stands out so you never miss one."),
        ("Visible ores underground", "Spot ores instantly while mining."),
        ("Ores and ancient debris", "Ancient debris is visible too."),
        ("Short sword", "Smaller, cleaner swords for better PvP visibility."),
        ("Short sword in hand", "The sword no longer blocks your view."),
        ("Clear pumpkin", "No more orange blur when wearing a pumpkin."),
        ("Low fire", "The fire overlay sits lower, with the full flame animation."),
    ]),
}

EXTRA_FILE = {
    "fliflight-low-shield": "02_fight.png",
    "fliflight-no-vignette": "02_night.png",
    "fliflight-clear-water": "02_underwater.png",
    "fliflight-clear-lava": "02_nether.png",
    "fliflight-clear-spyglass": "02_zoom.png",
    "fliflight-clean-hotbar": "02_items.png",
    "fliflight-thin-totem": "02_fight.png",
    "fliflight-clear-powder-snow": "02_night.png",
    "fliflight-clear-pumpkin": "02_night.png",
}


def show(r, label):
    b = r.text.strip()
    print(f"    {label}: {r.status_code} {b[:90] if b else ''}")


for slug, (pid, titles) in PLAN.items():
    print("=" * 64)
    print(f"[{slug}] {pid}")
    p = requests.get(f"{API}/project/{pid}", headers=HDR).json()
    gal = p.get("gallery") or []
    print(f"    current gallery: {len(gal)} items")

    # 1. upload the extra image if this pack has one and it is not there yet
    extra = EXTRA_FILE.get(slug)
    if extra:
        path = os.path.join(PACKS, slug, "gallery", extra)
        if os.path.exists(path):
            with open(path, "rb") as f:
                data = f.read()
            idx = len(gal)
            title, desc = titles[idx] if idx < len(titles) else ("", "")
            r = requests.post(f"{API}/project/{pid}/gallery", headers={**HDR, "Content-Type": "image/png"},
                              params={"ext": "png", "featured": "false", "ordering": idx,
                                      "title": title, "description": desc}, data=data)
            show(r, f"add {extra} (#{idx})")
            time.sleep(1)
            p = requests.get(f"{API}/project/{pid}", headers=HDR).json()
            gal = p.get("gallery") or []

    # 2. title every image + feature the first one
    for i, item in enumerate(gal):
        t, d = titles[i] if i < len(titles) else (f"Image {i+1}", "")
        if item.get("title") == t and item.get("featured") == (i == 0) and item.get("description") == d:
            print(f"    [{i}] already ok")
            continue
        r = requests.patch(f"{API}/project/{pid}/gallery", headers=HDR, params={"url": item["url"]},
                           json={"title": t, "description": d, "featured": i == 0, "ordering": i})
        show(r, f"[{i}] {t[:38]}")
        time.sleep(0.6)

    # 3. verify
    p = requests.get(f"{API}/project/{pid}", headers=HDR).json()
    gal = p.get("gallery") or []
    titled = sum(1 for g in gal if g.get("title"))
    feat = sum(1 for g in gal if g.get("featured"))
    print(f"    -> {len(gal)} images, {titled} titled, {feat} featured, status={p['status']}")

print("\nDONE")
