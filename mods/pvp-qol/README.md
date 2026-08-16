# PvP Essentials QoL (Fabric mod)

Client-side PvP quality-of-life mod for Minecraft **1.21.4**.

## Features
- **HUD** — FPS, ping, and coordinates in the top-left corner.
- **Lowered fire** — pushes the burning-overlay flame further down so it stays out of your view.
- **No pumpkin blur** — removes the carved-pumpkin screen overlay.

All features are toggleable via `config/pvpqol.json` (generated on first launch).

## Install
1. Install the [Fabric Loader](https://fabricmc.net/use/) for Minecraft 1.21.4.
2. Install the [Fabric API](https://modrinth.com/mod/fabric-api) (required).
3. Drop `pvp-qol-<version>.jar` into your `.minecraft/mods/` folder.

## Config (`config/pvpqol.json`)
| Key | Default | Meaning |
|---|---|---|
| `hudEnabled` | `true` | Enable the HUD |
| `hudShowFps` | `true` | Show FPS line |
| `hudShowPing` | `true` | Show ping line |
| `hudShowCoords` | `true` | Show XYZ line |
| `hudShadow` | `true` | Draw HUD text with shadow |
| `lowerFireEnabled` | `true` | Lower the fire overlay |
| `fireLowerOffset` | `0.35` | How far down to push the flame (0 = vanilla) |
| `noPumpkinBlur` | `true` | Remove pumpkin blur |

## Build
```bash
gradle build          # outputs build/libs/pvp-qol-<version>.jar
```

## License
All Rights Reserved — see LICENSE.
