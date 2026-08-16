# Custom Crosshair (Fabric mod)

Client-side customizable crosshair for Minecraft **1.21.4** PvP. No more downloading a new resource pack for every crosshair — change it directly.

## Features
- **5 shapes**: cross, dot, x, circle, t
- **Color** (ARGB int), **size**, **thickness**, **center gap**
- Rendered in first person, vanilla crosshair hidden while enabled.

## Config (`config/custom-crosshair.json`)
| Key | Default | Meaning |
|---|---|---|
| `enabled` | `true` | Replace vanilla crosshair |
| `shape` | `"cross"` | `cross`, `dot`, `x`, `circle`, `t` |
| `color` | `0xFF00FF00` | ARGB color (0xFF000000 = black, 0xFFFF0000 = red, 0xFF00FF00 = green) |
| `size` | `10` | Radius / half-length in pixels |
| `thickness` | `2` | Line thickness |
| `gap` | `2` | Center gap (cross/t/x) |

## Install
1. Install the [Fabric Loader](https://fabricmc.net/use/) for Minecraft 1.21.4.
2. Install the [Fabric API](https://modrinth.com/mod/fabric-api) (required).
3. Drop `custom-crosshair-<version>.jar` into your `.minecraft/mods/` folder.

## Build
```bash
gradle build          # outputs build/libs/custom-crosshair-<version>.jar
```

## License
All Rights Reserved — see LICENSE.
