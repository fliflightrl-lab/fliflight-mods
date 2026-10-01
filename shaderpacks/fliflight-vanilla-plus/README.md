# Fliflight Vanilla Plus — shader pack

Pack de shader client **Vanilla+** : fidèle au style Minecraft, juste plus beau. Aucun effet
"cinématique" lourd — on garde le look d'origine et on l'améliore.

- **Version** : v0.2
- **Cible** : Minecraft Java 1.21.x — OptiFine / Iris
- **Format** : OptiFine shader pack (`#version 120`, GLSL legacy compatible)
- **Vérifié** : compilé et chargé par OptiFine 1.21.4_HD_U_J4_pre2 — 26 programmes, 0 erreur GLSL

## Effets

| Effet | Détail |
|---|---|
| **Aucun brouillard** | eau, lave, poudreuse, distance |
| **Bloom** | bright-pass + 2 passes de flou gaussien (5 passes) |
| **Ombres** | shadowmap 2048, reconstruction du monde, normal-offset anti-acné |
| **Feuillage qui ondule** | herbe, feuilles, fleurs, cultures — bruit 2D, seuls les sommets bougent |
| **Ciel + soleil** | halo autour du soleil, chaleur à l'horizon au lever/coucher |
| Étalonnage | saturation +12 %, contraste +5 %, luminosité +2 %, netteté |

Tout se règle dans `shaders/lib/config.glsl` :

```glsl
#define BLOOM_STRENGTH    0.45
#define BLOOM_THRESHOLD   0.68
#define SHADOW_STRENGTH   0.85
#define WAVE_SCALE        1.00
#define SUN_HALO_STRENGTH 0.55
```

## Structure

```
shaders/
  shaders.properties        shadowMapResolution, shadowDistance, sunPathRotation
  block.properties          IDs de blocs pour le waving (mc_Entity.x)
  lib/config.glsl           toggles + reglages
  lib/space.glsl            ToNDC / ToWorld / ToShadow + getSunDir()
  lib/waves.glsl            bruit + WavingBlocks()
  lib/vs.glsl               vertex partage (waves + position monde)
  lib/vs_shadow.glsl        vertex de la passe d'ombre
  lib/fs_shadow.glsl        fragment de la passe d'ombre (alpha-test)
  lib/fs_lit.glsl           eclaire + ombres
  lib/fs_tex.glsl           texture non eclaire
  lib/fs_basic.glsl         non texture
  lib/fs_skybasic.glsl      ciel procedural + halo solaire
  lib/fs_skytextured.glsl   soleil / lune
  lib/vs_fullscreen.glsl    vertex des passes plein ecran
  gbuffers_*.vsh/.fsh       19 programmes
  shadow.vsh/.fsh           passe d'ombre
  composite.fsh             bright-pass -> colortex1
  composite1/2.fsh          flou H/V rayon serre (colortex1 <-> colortex2)
  composite3/4.fsh          flou H/V rayon large
  final.fsh                 scene + bloom + etalonnage -> ecran
```

## Chaine de buffers (bloom)

```
gbuffers   -> colortex0   (scene)
composite  -> colortex1   (bright-pass)        /*DRAWBUFFERS:1*/
composite1 -> colortex2   (flou H, rayon 1.5)  /*DRAWBUFFERS:2*/
composite2 -> colortex1   (flou V, rayon 1.5)
composite3 -> colortex2   (flou H, rayon 4.0)
composite4 -> colortex1   (flou V, rayon 4.0)
final      -> ecran       (colortex0 + colortex1)
```

## Pourquoi pas de brouillard automatiquement

Dans OptiFine/Iris, **le brouillard est appliqué par les shaders du pack** (`linear_fog`),
pas par le jeu. Un pack qui ne l'appelle pas n'a pas de brouillard. C'est exactement ce
qu'aucun resource pack ne peut faire.

## Installer / tester

1. Le `.zip` va dans `.minecraft/shaderpacks/`.
2. En jeu : **Options → Video Settings → Shaders** → **FliflightVanillaPlus-v0.2**.
3. OptiFine (ou Iris + Sodium).

## Régler l'intensité

Tout est dans `shaders/lib/config.glsl` (toggles + intensités) et en haut de `shaders/final.fsh`
(étalonnage, `SATURATION` / `CONTRAST` / `BRIGHTNESS` / `SHARPNESS`).
`1.0` = valeur d'origine ; `SHARPNESS 0.0` = pas de netteté.

## Pièges (leçons apprises)

- **`#include` OptiFine exige le nom COMPLET avec extension** : `"/lib/fs_lit.glsl"`.
- **`/*DRAWBUFFERS:N*/` est obligatoire** dans tout `composite*.fsh`, sinon `gl_FragData[0]`
  va sur colortex0 et **écrase la scène**.
- **Ne jamais générer un littéral flottant par concaténation** : `f"{radius}.0"` avec
  `radius=1.5` produit `1.5.0` → `syntax error, unexpected floating point constant`.
- **Les ombres ont besoin du normal-offset** (`worldPos + normal * 0.06`) contre l'acné.
- **`sunAngle`** OptiFine : 0.0 = lever, 0.25 = midi, 0.5 = coucher, 0.75 = minuit.
- **`istopv`** (sommet haut d'une plante) :
  `gl_MultiTexCoord0.t < mc_midTexCoord.t ? 1.0 : 0.0`.
- Les `gbuffers_*` écrivent dans `gl_FragData[0]` ; `final` écrit dans `gl_FragColor`.

## Vérifier sans lancer le jeu à la main

Un shader qui ne compile pas = écran noir silencieux. Pour tester la compilation :

1. Construire le classpath vanilla, puis lancer OptiFine en launchwrapper :
   `java -cp "<OptiFine.jar>;<launchwrapper-of.jar>;<classpath vanilla>" \
    net.minecraft.launchwrapper.Launch --tweakClass optifine.OptiFineTweaker --username X \
    --version <ver> --gameDir <mc> --assetsDir <mc>/assets --assetIndex 19 \
    --uuid <uuid> --accessToken 0 --userType legacy --quickPlaySingleplayer "<monde>"`
2. OptiFine logue le nom exact du pack chargé. Si `optionsof.txt` (`shaderPack=`) est ignoré,
   copier le contenu du nouveau pack **sous le nom du pack déjà sélectionné**.
3. Lire `logs/latest.log` : `Program loaded: <nom>` par programme, et
   `Error compiling fragment shader:` + numéros de ligne pour les erreurs.

## Roadmap

- v0.3 : ombres filtrées (PCF), feuillage plus vivant, ombres colorées
- v0.4 : eau avec vagues + reflets, ciel étoilé amélioré
- v0.5 : lueur (glow) sur les entités, lumière directionnelle
