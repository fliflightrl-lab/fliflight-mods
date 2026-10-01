# Fliflight Vanilla Plus - shader pack

Pack de shader client **Vanilla+** : fidele au style Minecraft, juste plus beau.
Version **v0.3 « Potato »** : la meme image qu'en v0.2, mais legere.

- **Cible** : Minecraft Java 1.21.x - OptiFine / Iris
- **Format** : OptiFine shader pack (`#version 120`, GLSL legacy)
- **Verifie** : OptiFine 1.21.4_HD_U_J4_pre2 - 24 programmes charges, 0 erreur GLSL

## Effets

| Effet | Detail |
|---|---|
| **Aucun brouillard** | eau, lave, poudreuse : visibilite totale |
| **Bloom** | bright-pass + 1 flou horizontal + 1 flou vertical (5 taps) |
| **Ombres** | shadowmap 1024, ombres 64 blocs, fondu de sortie |
| **Feuillage qui ondule** | herbe, feuilles, fleurs, cultures |
| **Ciel + soleil** | halo solaire + chaleur a l'horizon |
| **Brume d'horizon** | le terrain tres lointain refond vers la couleur du ciel |
| Etalonnage | saturation +12 %, contraste +5 %, luminosite +2 %, nettete |

## Profil Potato (v0.3) : ce qui a change

| | v0.2 | v0.3 Potato |
|---|---|---|
| Passes de bloom | 5 (2 flous separes) | **3** (1 flou H + 1 flou V) |
| Lectures de texture pour le bloom | **45 / pixel** | **11 / pixel** |
| Resolution de la shadowmap | 2048 | **1024** (4x moins de pixels a rastériser) |
| Distance des ombres | 128 blocs | **64 blocs** |
| Fondu des ombres en sortie | non | **oui** |
| Early-out hors de portee d'ombre | non | **oui** (aucune lecture) |

Pour revenir a la qualite v0.2 : decommenter `#define HIGH_QUALITY` dans `lib/config.glsl`
(remet 128 blocs d'ombres ; la shadowmap se regle dans `shaders.properties`).

## Corrige en v0.3

- **Voile noir au loin au niveau du sol** : trois causes cumulees.
  1. `shadow.fsh` utilisait `uniform sampler2D tex`, alors qu'OptiFine attend **`texture`** dans
     un programme d'ombre. Le sampler non lie rendait le test alpha faux : la shadowmap pouvait
     se retrouver vide, et tout fragment couvert etait alors considere **a l'ombre**.
  2. Aucun **fondu de sortie** : au bord des 128 blocs la zone d'ombre s'arretait net -> bande sombre.
  3. Le brouillard du jeu est supprime, or c'est lui qui lavait le terrain lointain vers la couleur
     du ciel. Sans lui, le sol lointain reste sombre -> **brume d'horizon** ajoutee (les 28 % les
     plus lointains uniquement : rien de proche, sous l'eau ou dans la lave n'est touche).
- **`error C1038: declaration of "cameraPosition" conflicts with previous declaration`** :
  `cameraPosition` etait declare dans `lib/haze.glsl` **et** dans `lib/fs_lit.glsl`. Les 8 programmes
  qui utilisent `fs_lit` ne compilaient plus. Un uniform ne se declare qu'une fois par chaine d'include.

## Structure

```
shaders/
  shaders.properties        shadowMapResolution=1024, shadowDistance=64
  block.properties          IDs de blocs pour le waving
  lib/config.glsl           profil + toggles + intensites
  lib/haze.glsl             brume d'horizon (applyHaze)
  lib/space.glsl            ToNDC / ToWorld / ToShadow + getSunDir()
  lib/waves.glsl            bruit + WavingBlocks()
  lib/vs.glsl               vertex partage
  lib/vs_shadow.glsl        vertex de la passe d'ombre
  lib/fs_shadow.glsl        fragment d'ombre (sampler `texture`)
  lib/fs_lit.glsl           eclaire + ombres + brume
  lib/fs_tex.glsl           texture + brume
  lib/fs_basic.glsl         non texture + brume
  lib/fs_skybasic.glsl      ciel procedural + halo solaire
  lib/fs_skytextured.glsl   soleil / lune
  lib/vs_fullscreen.glsl    vertex des passes plein ecran
  gbuffers_*.vsh/.fsh       19 programmes
  shadow.vsh/.fsh
  composite.fsh             bright-pass -> colortex1
  composite1.fsh            flou H (5 taps) colortex1 -> colortex2
  composite2.fsh            flou V (5 taps) colortex2 -> colortex1
  final.fsh                 scene + bloom + etalonnage -> ecran
```

## Reglages (`lib/config.glsl`)

```glsl
#define BLOOM_STRENGTH    0.45
#define BLOOM_THRESHOLD   0.68
#define BLOOM_SPREAD      2.5
#define SHADOW_STRENGTH   0.85
#define WAVE_SCALE        1.00
#define SUN_HALO_STRENGTH 0.55
#define HORIZON_HAZE_START    0.72   // 0.0 = brume des le premier bloc
#define HORIZON_HAZE_STRENGTH 0.85   // 0.0 = desactive
```

## Valider avant de lancer le jeu

```bash
python scripts/validate_shader.py shaderpacks/fliflight-vanilla-plus
```

Il attrape les erreurs qui donnent un **ecran noir silencieux** : `#include` sans extension,
`DRAWBUFFERS` manquant, litteraux flottants malformes, varyings absents du vertex,
**uniformes declares en double** et sampler d'ombre mal nomme.

## Tester la compilation sans jouer a la main

1. Lancer OptiFine en launchwrapper (classpath vanilla + jars OptiFine) :
   `java -cp "<OptiFine.jar>;<launchwrapper-of.jar>;<classpath vanilla>" \
    net.minecraft.launchwrapper.Launch --tweakClass optifine.OptiFineTweaker --username X \
    --version <ver> --gameDir <mc> --assetsDir <mc>/assets --assetIndex 19 \
    --uuid <32hex> --accessToken 0 --userType legacy --quickPlaySingleplayer "<monde>"`
2. OptiFine logue le nom du pack **deja selectionne**. Si `optionsof.txt` est ignore, copier le
   contenu du nouveau pack **sous ce nom** pour forcer le test.
3. Lire `logs/latest.log` : `Program loaded: <nom>` par programme ; en cas d'echec,
   `Error compiling fragment shader:` puis `1(<ligne>) : error C....` avec le numero de ligne.

## Roadmap

- v0.4 : ombres filtrees (PCF) en option, eau avec vagues, ciel etoile
- v0.5 : lueur sur les entites, lumiere directionnelle
