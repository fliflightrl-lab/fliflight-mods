# PvP HUD (Fabric mod)

Client-side PvP HUD for Minecraft **1.21.4**: FPS, ping, coordinates and **clicks-per-second (CPS)** in the top-left corner.

## Features
- **FPS** — current frame rate.
- **Ping** — latency to the current server.
- **Coordinates** — XYZ position.
- **CPS** — left/right clicks per second (sliding 1-second window).

All lines are toggleable via `config/pvphud.json` (generated on first launch).

## Install
1. Install the [Fabric Loader](https://fabricmc.net/use/) for Minecraft 1.21.4.
2. Install the [Fabric API](https://modrinth.com/mod/fabric-api) (required).
3. Drop `pvphud-<version>.jar` into your `.minecraft/mods/` folder.

## Config (`config/pvphud.json`)
| Key | Default | Meaning |
|---|---|---|
| `hudEnabled` | `true` | Enable the HUD |
| `hudShowFps` | `true` | Show FPS line |
| `hudShowPing` | `true` | Show ping line |
| `hudShowCoords` | `true` | Show XYZ line |
| `hudShowCps` | `true` | Show CPS line (left / right) |
| `hudShadow` | `true` | Draw HUD text with shadow |

## Build
```bash
gradle build          # outputs build/libs/pvphud-<version>.jar
```

## License
All Rights Reserved — see LICENSE.
