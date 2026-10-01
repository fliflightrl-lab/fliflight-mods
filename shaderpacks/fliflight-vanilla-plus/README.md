# Fliflight Vanilla Plus - shader pack

Pack de shader client **Vanilla+** : fidele au style Minecraft, juste plus beau.
Version **v0.3.1 « Potato »** : la meme image, en leger.

- **Cible** : Minecraft Java 1.21.x - OptiFine / Iris
- **Format** : OptiFine shader pack (`#version 120`, GLSL legacy)
- **Verifie** : OptiFine 1.21.4_HD_U_J4_pre2 - 24 programmes, 0 erreur GLSL, dans les
  deux configurations (brume desactivee et active)

## Effets actifs

| Effet | Detail |
|---|---|
| **Aucun brouillard** | eau, lave, poudreuse : visibilite totale |
| **Bloom** | bright-pass + 1 flou horizontal + 1 flou vertical (5 taps) |
| **Ombres** | shadowmap 1024, portee 64 blocs, fondu de sortie, early-out |
| **Feuillage qui ondule** | herbe, feuilles, fleurs, cultures |
| **Ciel + soleil** | halo solaire + chaleur a l'horizon |
| Etalonnage | saturation +12 %, contraste +5 %, luminosite +2 %, nettete |

**Brume d'horizon : DESACTIVEE par defaut.** Voir la section suivante.

## Corrige en v0.3.1 : l'ecran tout bleu de la v0.3

La brume d'horizon de la v0.3 calculait sa distance ainsi :

```glsl
float dist = length(worldPos - cameraPosition);
float start = far * HORIZON_HAZE_START;      // <-- FAUX
```

En supposant que `far` vaut la distance de rendu en blocs. **Ce n'est pas le cas** : la valeur
peut etre tres petite (c'est le plan lointain de la projection, pas la distance de rendu).
`start` tombait alors a quelques blocs et **tout l'ecran passait a la couleur du ciel**. Meme
symptome si `cameraPosition` vaut 0 : `length(worldPos)` mesure alors la distance depuis
l'origine du monde (des milliers de blocs).

**Correction** : plus aucune dependance a `far` ni `cameraPosition`. En espace vue la camera
est a l'origine, donc `length(viewPos)` **est** la distance a la camera. Le vertex shader
l'emet en varying (`viewDist`) et les seuils sont exprimes **en blocs** dans la config :

```glsl
#define HAZE_START_BLOCKS 120.0
#define HAZE_END_BLOCKS   300.0
#define HAZE_STRENGTH     0.85
```

C'est deterministe : aucun uniform ne peut inverser le resultat. Et `viewDist` sert aussi au
test de portee des ombres, qui dependait de `cameraPosition`.

## Corrige en v0.3 : le voile noir au loin

- `shadow.fsh` utilisait `uniform sampler2D tex` : dans un programme d'ombre OptiFine le
  sampler s'appelle **`texture`**. Non lie, le test alpha jetait tous les fragments, la
  shadowmap restait vide, et tout ce qu'elle couvre lisait « a l'ombre ».
- Aucun fondu en sortie d'ombre -> bande sombre dure au bord des 128 blocs.
- Le brouillard du jeu (supprime) est ce qui lavait le terrain lointain vers le ciel.

## Profil Potato (v0.3+)

| | v0.2 | Potato |
|---|---|---|
| Passes de bloom | 5 | **3** |
| **Lectures de texture pour le bloom** | **45 / pixel** | **11 / pixel** |
| Resolution shadowmap | 2048 | **1024** |
| Portee des ombres | 128 blocs | **64 blocs** |
| Fondu de sortie d'ombre | non | **oui** |
| Early-out hors portee | non | **oui** |

Pour la qualite v0.2 : decommenter `#define HIGH_QUALITY` dans `lib/config.glsl`.

## Structure

```
shaders/
  shaders.properties        shadowMapResolution=1024, shadowDistance=64
  block.properties          IDs de blocs pour le waving
  lib/config.glsl           profil + toggles + intensites
  lib/haze.glsl             brume d'horizon (applyHaze), opt-in
  lib/space.glsl            ToNDC / ToWorld / ToShadow + getSunDir()
  lib/waves.glsl            bruit + WavingBlocks()
  lib/vs.glsl               vertex partage : emet vWorldPos ET viewDist
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
#define BLOOM_STRENGTH    0.45   // 0.0 = bloom off
#define BLOOM_THRESHOLD   0.68
#define BLOOM_SPREAD      2.5
#define SHADOW_STRENGTH   0.85   // 0.0 = ombres off
#define WAVE_SCALE        1.00
#define SUN_HALO_STRENGTH 0.55
//#define HORIZON_HAZE            // decommenter pour activer la brume d'horizon
#define HAZE_START_BLOCKS 120.0
#define HAZE_END_BLOCKS   300.0
#define HAZE_STRENGTH     0.85
```

## Valider avant de lancer le jeu

```bash
python scripts/validate_shader.py shaderpacks/fliflight-vanilla-plus
```

Attrape les erreurs qui donnent un **ecran noir silencieux** : `#include` sans extension,
`DRAWBUFFERS` manquant, litteraux flottants malformes, varyings absents du vertex,
**uniformes declares en double** (error C1038), sampler d'ombre mal nomme.

## Tester la compilation sans jouer a la main

Lancer OptiFine en launchwrapper (classpath vanilla + jars OptiFine + `--quickPlaySingleplayer`,
qui force la compilation des `gbuffers_*`), puis lire `logs/latest.log` :
`Program loaded: <nom>` par programme, et `Error compiling fragment shader:` + `<ligne> : error C....`
en cas d'echec. OptiFine logue le nom du pack **deja selectionne** : si `optionsof.txt` est
ignore, copier le contenu du nouveau pack sous ce nom pour forcer le test.
**Tester chaque combinaison de `#define`** : une config qui compile n'implique pas l'autre.

## Lecons apprises (a ne pas refaire)

- Un uniform existe mais peut valoir **0** : ne jamais faire reposer un seuil visuel sur sa valeur.
- Preferer une donnee calculee dans le vertex (`viewDist`) a un uniform d'etat du moteur.
- Un effet visuel invisible pour l'auteur ne doit pas etre livre **actif** : opt-in d'abord.

## Roadmap

- v0.4 : ombres filtrees (PCF) en option, eau avec vagues, ciel etoile
