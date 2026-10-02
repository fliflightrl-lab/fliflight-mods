# Everlight — See in the Dark · v1.0.0

A see-in-the-dark resource pack for Minecraft Java Edition. One job: make the world readable
everywhere, without touching anything else.

## What it does

- Replaces the **light map**, so low light levels stay bright instead of fading to black
- **Caves and the night surface** become as readable as a sunlit plain — that is where vanilla is
  genuinely black, and where this pack does the most
- The **Nether and the End** get a lift too, but vanilla already lights them reasonably well, so
  the difference there is smaller
- **Torch light is perfectly steady** — the flicker is removed entirely
- **Night stays slightly cooler and dimmer than day**, so the world keeps a day/night cycle
  instead of looking permanently noon

## Requirements — pick one

The light map is **not a vanilla asset**: Minecraft generates it at runtime (the 1.21.4 client
jar ships only `assets/minecraft/shaders/core/lightmap.fsh`). Overriding it needs one of:

| Option | For |
|---|---|
| **OptiFine** | the classic route |
| **Polytone** | Fabric / NeoForge players on Sodium + Iris |

Both light maps ship in the same zip. Without either, the pack does nothing.

## Install

1. Install **OptiFine**, or **Polytone** on Fabric/NeoForge.
2. Drop the `.zip` into `.minecraft/resourcepacks` (do not unzip).
3. Enable it in **Options → Resource Packs**.

## Proof

| Preset | Pixels changed | Brightness gain |
|---|---|---|
| Cave, same spot | **95 %** | **+54 / 255** |
| Same spot at night | 34 % | +16 / 255 |

Both measured on real captures, not estimated. The Nether and the End were also measured: +8.8
and +6.8 — small, because those dimensions are already well lit in vanilla. They are shipped as
plain scenery rather than passed off as before/after comparisons.

## Servers

On competitive servers this is a visual advantage, so check the rules before using it.

## Links

- **CurseForge** — the download page
- **Modrinth** — https://modrinth.com/resourcepack/fliflight-everlight
- Support the work — https://ko-fi.com/fliflight
- Everything else — https://linktr.ee/fliflight

## Version 1.0.0

Initial release: bright light map for all three dimensions, flicker-free torch light, day/night
kept readable. Ships light maps for both OptiFine and Polytone.
