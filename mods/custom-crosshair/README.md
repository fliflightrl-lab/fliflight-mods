# Custom Crosshair (Fabric mod)

Client-side customizable crosshair for Minecraft **1.21.4** PvP. No more downloading a new resource pack for every crosshair — change it directly in-game.

## Features
- **In-game settings screen** — press **C** (rebindable in Options → Controls → Key Binds) to open it.
- **5 shapes**: cross, dot, x, circle, t — with live preview.
- **Color**: 8 preset colors + RGB sliders.
- **Size**, **thickness** and **center gap** sliders.
- **6 ready-made presets**: Classic Cross, Dot, X, Circle, T, Valorant.
- Vanilla crosshair hidden while enabled.

## Install
1. Install the [Fabric Loader](https://fabricmc.net/use/) for Minecraft 1.21.4.
2. Install the [Fabric API](https://modrinth.com/mod/fabric-api) (required).
3. Drop `custom-crosshair-<version>.jar` into your `.minecraft/mods/` folder.

## Usage
Press **C** in-game (or rebind it) to open the settings screen. Every change applies instantly and is saved to `config/custom-crosshair.json`.

## Build
```bash
gradle build          # outputs build/libs/custom-crosshair-<version>.jar
```

## License
All Rights Reserved — see LICENSE.
