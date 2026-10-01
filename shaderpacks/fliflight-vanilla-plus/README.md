# Fliflight Vanilla Plus — shader pack

Pack de shader client **Vanilla+** : fidèle au style Minecraft, juste plus beau. Aucun effet
"cinématique" lourd — on garde le look d'origine et on l'améliore.

- **Version** : v0.1
- **Cible** : Minecraft Java 1.21.x — OptiFine / Iris
- **Format** : OptiFine shader pack (`#version 120`, GLSL legacy compatible)

## Ce que fait la v0.1

| Effet | Détail |
|---|---|
| **Aucun brouillard** | Le pack n'appelle jamais `linear_fog` → eau, lave, poudreuse et distance : plus de brouillard. C'est le gros morceau. |
| **Saturation** | +12 % (paramètre `SATURATION`) |
| **Contraste** | +5 % autour du gris moyen (`CONTRAST`) |
| **Luminosité** | +2 % (`BRIGHTNESS`) |
| **Netteté** | Unsharp mask léger, 4 échantillons voisins (`SHARPNESS` 0.30) |

## Structure

```
shaders/
  shaders.properties
  lib/vs.glsl           vertex partagé (position, texcoord, lightmap, couleur, normale)
  lib/fs_lit.glsl       fragment éclairé   : texture x couleur x lightmap
  lib/fs_tex.glsl       fragment non éclairé : texture x couleur
  lib/fs_basic.glsl     fragment sans texture : couleur x lightmap
  lib/fs_sky.glsl       ciel
  gbuffers_*.vsh/.fsh   19 programmes (basic, line, textured, terrain, water, entities,
                        hand, block, clouds, weather, skybasic, skytextured,
                        damagedblock, beaconbeam, armor_glint, spidereyes, ...)
  final.vsh/.fsh        étalonnage + netteté (passe plein écran)
```

`final.fsh` lit `colortex0` (la scène rendue) et applique l'étalonnage. Les `gbuffers_*`
écrivent dans `colortex0` — c'est eux qui décident du brouillard (ils ne l'appliquent pas).

## Pourquoi pas de brouillard automatiquement

Dans OptiFine/Iris, **le brouillard est appliqué par les shaders du pack** (`linear_fog`),
pas par le jeu. Un pack qui ne l'appelle pas n'a pas de brouillard. C'est exactement ce
qu'aucun resource pack ne peut faire.

## Installer / tester

1. Le `.zip` va dans `.minecraft/shaderpacks/` (déjà fait).
2. En jeu : **Options → Video Settings → Shaders** → sélectionner **FliflightVanillaPlus-v0.1**.
3. Nécessite **OptiFine** (ou Iris + Sodium).

## Régler l'intensité

Tout est en haut de `shaders/final.fsh` :

```glsl
#define SATURATION 1.12
#define CONTRAST   1.05
#define BRIGHTNESS 1.02
#define SHARPNESS  0.30
```

- `SATURATION 1.0` = couleurs d'origine
- `CONTRAST 1.0` = contraste d'origine
- `BRIGHTNESS 1.0` = luminosité d'origine
- `SHARPNESS 0.0` = pas de netteté

## Pièges (leçons apprises)

- **Un `#include` OptiFine exige le nom de fichier COMPLET avec l'extension** :
  `#include "/lib/fs_lit.glsl"`, pas `#include "/lib/fs_lit"`. Sans extension le shader ne
  compile pas → écran noir / crash.
- Les `gbuffers_*` écrivent dans `gl_FragData[0]` ; `final` écrit dans `gl_FragColor`.
- Toujours vérifier les `#include` (fichier cible existant) et l'équilibre des accolades
  avant de livrer un pack : une erreur GLSL = écran noir, pas un message d'erreur lisible.

## Roadmap

- v0.2 : bloom (bright-pass + blur flou gaussien sur plusieurs passes)
- v0.3 : ombres (passe `shadow` + shadowmap)
- v0.4 : feuillage qui ondule, eau avec vagues
- v0.5 : ciel/soleil custom
