# Fliflight Vanilla Plus - shader pack

Pack de shader client **Vanilla+**, profil **Potato**. Version **v0.7**.

- **Cible** : Minecraft Java 1.21.x - OptiFine / Iris
- **Verifie** : OptiFine 1.21.4_HD_U_J4_pre2 - **21 programmes, 0 erreur**
- SHA256 du zip livre = SHA256 du zip installe

**Principe directeur : tout le rendu ajoute est du calcul dans des shaders qui existent deja.**
Aucune passe plein ecran en plus, aucune lecture de texture en plus. On reste a 2 passes.

## Effets

| Effet | Detail | Cout |
|---|---|---|
| **Aucun brouillard** | eau, lave, poudreuse | — |
| **Bloom** | seuil + flou H dans `composite`, flou V dans `final` | 2 passes |
| **Feuillage qui ondule** | herbe, feuilles, fleurs, cultures | vertex |
| **Eau animee** | houle sur la face du dessus | vertex |
| **Lumiere teintee** | torches chaudes, ciel froid | 0 (aucune lecture en plus) |
| **Lumiere directionnelle** | le cote expose au soleil prend la couleur de l'heure | 0 |
| **Ciel** | halo solaire, bande chaude a l'aube/crepuscule, etoiles, halo lunaire | ciel seulement |
| **Etalonnage par heure** | nuits froides, aube/crepuscule chauds | 0 |

## A. Lumiere teintee (v0.7)

Le pack prenait le lightmap vanilla brut. Il est maintenant teinte :

```glsl
vec3 tint = (BLOCK_TINT * blockAmt + SKY_TINT * skyAmt) / max(blockAmt + skyAmt, 0.0001);
light *= mix(vec3(1.0), tint, LIGHT_TINT_STRENGTH);
```

`lmCoord.x` = lumiere de bloc, `lmCoord.y` = lumiere du ciel. On teinte **l'echantillon unique**
d'apres leur poids relatif : **aucune lecture de texture supplementaire**. Les deux teintes ont une
luminance de ~1.0, donc teinter change la couleur **sans** changer la luminosite globale.

```glsl
#define BLOCK_TINT vec3(1.18, 0.98, 0.76)   // torches
#define SKY_TINT   vec3(0.91, 1.00, 1.24)   // ciel
#define LIGHT_TINT_STRENGTH 0.65            // 0.0 = couleurs vanilla
```

**Lumiere directionnelle** : le cote expose au soleil prend la couleur de l'heure (dore au coucher,
bleute la nuit), ponderee par la lumiere du ciel — donc l'interieur n'est pas touche. C'est ce qui
remplace une bonne part de l'interet visuel des ombres, **sans passe d'ombre**.

```glsl
#define DIRECTIONAL_STRENGTH 0.35
```

## B. Eau animee (v0.7)

`lib/vs_water.glsl` remplace `vs.glsl` pour `gbuffers_water` et `gbuffers_hand_water`.

```sl
if (vNormal.y > 0.5) {   // face du dessus seulement : les parois ne bougent pas
    float w = sin(wPos.x * 0.65 + frameTimeCounter * WATER_WAVE_SPEED)
            + cos(wPos.z * 0.55 + frameTimeCounter * WATER_WAVE_SPEED * 0.74);
    wPos.y += w * WATER_WAVE_HEIGHT;
}
```

**Point cle** : la houle est fonction de la **position monde**, donc elle est **continue d'un chunk a
l'autre** — aucune couture visible aux frontieres. Une fonction de la position locale ferait sauter
la surface a chaque bord de chunk.

```glsl
#define WATER_WAVE_HEIGHT 0.10   // amplitude en blocs (0.10 = subtil, 0.25 = tres agite)
#define WATER_WAVE_SPEED  1.15
```

## C. Ciel (v0.7)

`lib/fs_skybasic.glsl` ajoute :

- **halo solaire** (existant, `SUN_HALO_STRENGTH`),
- **bande chaude a l'horizon cote soleil** : rouge profond a l'aube/crepuscule, plus douce en
  journee (`DUSK_STRENGTH`),
- **etoiles** : bruit par cellule de direction, **sans branchement** (`step(0.988, h)`) donc pas de
  divergence de warp. Fondues par la nuit et par `worldDir.y` pour qu'elles s'effacent vers l'horizon,
- **halo lunaire** : la lune est a l'oppose du soleil, `pow(moonAmount, 24.0)`.

`final.fsh` ajoute un **etalonnage par heure** : nuits plus froides, aube/crepuscule plus chauds.

## Reglages (`lib/config.glsl`)

Tout est commentable un par un : `BLOOM`, `WAVES`, `CUSTOM_SKY`, `WATER_WAVES`, `STARS`,
`LIGHT_TINT`, `DIRECTIONAL_LIGHT`, `TIME_GRADE`. Plus `SHARPEN`, `HORIZON_HAZE`, `SHADOWS`
(desactives).

```glsl
#define BLOOM_STRENGTH      0.45   // 0.0 = bloom off -> il ne reste que la passe final
#define LIGHT_TINT_STRENGTH 0.65   // 0.0 = couleurs vanilla
#define DIRECTIONAL_STRENGTH 0.35  // 0.0 = pas de teinte directionnelle
#define WATER_WAVE_HEIGHT   0.10
#define STARS_STRENGTH      0.85
#define DUSK_STRENGTH       0.45
```

## Perf

| | v0.2 | v0.6 | **v0.7** |
|---|---|---|---|
| Passes plein ecran | 6 | 2 | **2** |
| **Lectures de texture / pixel** | **51** | 9 | **9** |
| Passe d'ombre | oui | non | **non** |
| Chemin rapide OptiFine (`alphaTest`) | non | oui | **oui** |
| Programmes charges | 26 | 21 | **21** |

v0.7 ajoute **six effets** sans ajouter une seule passe ni une seule lecture de texture.

## Valider, tester, livrer

```bash
python scripts/validate_shader.py shaderpacks/fliflight-vanilla-plus
python scripts/rebuild_shaderzip.py --test
bash scripts/of_compile_test.sh <etiquette>
python scripts/rebuild_shaderzip.py
sha256sum dist/shaderpacks/*.zip .minecraft/shaderpacks/*.zip   # integrite
```

**Verifier le NOMBRE de programmes charges** : OptiFine charge le pack deja selectionne, donc un
build de test ecrit sous un nouveau nom valide l'ancien code. Le mode `--test` ecrase tous les
`FliflightVanillaPlus-*.zip` presents pour rendre cela impossible.

## Lecons apprises

- **Verifier le nombre de programmes charges**, pas seulement l'absence d'erreur.
- **Ne jamais generer N fois la meme declaration locale** : sortir la logique dans une fonction.
- **Toujours verifier le referentiel** (espace vue / espace monde) : `gl_NormalMatrix` = vue.
- **Un uniform peut valoir 0** : deriver la donnee dans le vertex (`viewDist`, normale monde).
- **Les directives `shaders.properties` pesent plus lourd que le code** : `alphaTest.*` active le
  chemin rapide d'OptiFine (compare toujours avec un pack de reference).
- **Une animation liee a la geometrie doit dependre de la position MONDE**, jamais locale.
- **Un effet invisible pour l'auteur ne se livre pas actif**, et une combinaison cassee ne se livre pas.
