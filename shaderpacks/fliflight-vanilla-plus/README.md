# Fliflight Vanilla Plus - shader pack

Pack de shader client **Vanilla+**, profil **Potato**. Version **v0.8**.

- **Cible** : Minecraft Java 1.21.x - OptiFine / Iris
- **Verifie** : OptiFine 1.21.4_HD_U_J4_pre2 - **22 programmes, 0 erreur**, aucun avertissement

## Effets

| Effet | Detail |
|---|---|
| **Aucun brouillard** | eau, lave, poudreuse |
| **Bloom** | seuil + flou H dans `composite` (demi-resolution), flou V dans `final` |
| **Ombres** | shadowmap 1024, portee 64 blocs, biais proportionnel a la pente |
| **Feuillage qui ondule** | herbe, feuilles, fleurs, cultures |
| **Eau animee** | houle sur la face du dessus, ancree en position monde |
| **Lumiere teintee** | torches chaudes, ciel froid, sans lecture supplementaire |
| **Lumiere directionnelle** | le cote expose au soleil prend la couleur de l'heure |
| **Ciel** | halo solaire et lunaire, bande chaude a l'aube, etoiles |
| **Brume d'horizon** | refond le terrain tres lointain vers la couleur du ciel |
| **Etalonnage par heure** | nuits froides, aube et crepuscule chauds |

## v0.8 - LE FIX DES OMBRES : position monde absurde dans la passe d'ombre

C'etait la cause du **« voile noir / grosse ombre etrange face au soleil »**, et c'etait un bug
franc, pas un probleme de reglage. Dans `lib/vs_shadow.glsl` :

```glsl
vec4 viewPos = gl_ModelViewMatrix * gl_Vertex;
vec3 wPos = (gbufferModelViewInverse * viewPos).xyz;   // FAUX
```

**Dans une passe d'ombre, `gl_ModelViewMatrix` EST la matrice d'ombre** (`shadowModelView`), pas
celle du gbuffer. La multiplier par `gbufferModelViewInverse` donne une « position monde » qui n'en
est pas une. La shadowmap etait donc remplie de geometrie placee n'importe ou : une grosse ombre
incoherente, dont l'aspect dependait de l'orientation de la camera.

**Preuve** : BSL doit inverser **deux** matrices pour retrouver la position monde, ce qui prouve
que les matrices fixed-function de la passe d'ombre sont bien celles de l'ombre :

```glsl
vec4 position = shadowModelViewInverse * shadowProjectionInverse * ftransform();
```

Correction (une seule inversion suffit, `gl_Vertex` etant deja passe par la modelview d'ombre) :

```glsl
vec4 worldPos = shadowModelViewInverse * (gl_ModelViewMatrix * gl_Vertex);
```

C'est aussi la meme famille d'erreur que les deux precedentes : **un vecteur du mauvais
referentiel**, dont le symptome depend de la camera.

## v0.8 - Bloom en demi-resolution

```properties
size.buffer.colortex1=0.5 0.5
```

Syntaxe officielle OptiFine (doc de sp614x) : une taille en flottant est **relative** a la
resolution de rendu. La passe `composite` ecrit donc **4x moins de pixels**. Contraintes de la doc
respectees :

- seuls les programmes `prepare`/`deferred`/`composite` peuvent ecrire en taille fixe - `composite` ✓
- ecrire en taille fixe ET normale en meme temps est impossible - `composite` ecrit
  **uniquement** `colortex1` (`/*DRAWBUFFERS:1*/`) ✓

## Corriges en v0.8 (trouves par les avertissements OptiFine)

- **`Ambiguous shader option: SHADOW_DISTANCE`** : la macro etait definie deux fois (128.0 et 64.0
  sous `#ifdef HIGH_QUALITY`). Une macro ne se definit **qu'une fois** dans la chaine d'include.
- **`Block not found for name: minecraft:grass`** : ce nom n'existe plus depuis 1.20.3
  (renomme `short_grass`). Corrige dans `block.properties`.
- **Le script de build annulait la config** : il remettait tous les flags a off sauf ceux passes
  en argument. Il ne touche plus un flag que s'il est demande explicitement.

## Debug : verifier les avertissements, pas seulement les erreurs

```bash
grep -aE "Ambiguous|Block not found|Error compiling|error C[0-9]" <log>
```

Les avertissements d'OptiFine sont peu visibles mais revelateurs : `Ambiguous` signale une macro
definie plusieurs fois, `Block not found` une entree de `block.properties` obsolete.

## Perf

| | v0.2 | v0.5 | v0.6 | **v0.8** |
|---|---|---|---|---|
| Passes plein ecran | 6 | 3 | 2 | **2** |
| **Lectures de texture / pixel** | **51** | 12 | 9 | **9** |
| Pixels ecrits pour le bloom | plein ecran | plein ecran | plein ecran | **1/4** |
| Chemin rapide OptiFine (`alphaTest`) | non | non | oui | **oui** |
| Passe d'ombre | oui | non | non | **oui (64 blocs)** |
| Programmes charges | 26 | 22 | 21 | **22** |

Les ombres reajoutent une passe geometrique : si les FPS comptent plus que les ombres, commenter
`#define SHADOWS` dans `lib/config.glsl`.

## Reglages (`lib/config.glsl`)

```glsl
#define SHADOW_DISTANCE    64.0   // 128.0 pour plus loin (et moins de FPS)
#define SHADOW_STRENGTH    0.85   // 0.0 = ombres invisibles
#define SHADOW_BIAS_SLOPE  0.25   // monter si acne residuelle (0.5, 0.8)
#define BLOOM_STRENGTH     0.45   // 0.0 = bloom off
#define LIGHT_TINT_STRENGTH 0.65
#define DIRECTIONAL_STRENGTH 0.35
#define WATER_WAVE_HEIGHT  0.10
#define STARS_STRENGTH     0.85
#define HAZE_START_BLOCKS  120.0  // la brume commence ici
#define HAZE_END_BLOCKS    300.0
```

Chaque effet se coupe en commentant son `#define` : `BLOOM`, `SHADOWS`, `WAVES`, `CUSTOM_SKY`,
`WATER_WAVES`, `STARS`, `LIGHT_TINT`, `DIRECTIONAL_LIGHT`, `TIME_GRADE`, `HORIZON_HAZE`, `SHARPEN`.

## Valider, tester, livrer

```bash
python scripts/validate_shader.py shaderpacks/fliflight-vanilla-plus
python scripts/rebuild_shaderzip.py --test [--shadows] [--haze] [--sharpen]
bash scripts/of_compile_test.sh <etiquette>
python scripts/rebuild_shaderzip.py
sha256sum dist/shaderpacks/*.zip .minecraft/shaderpacks/*.zip
```

**Controler le NOMBRE de programmes charges** : OptiFine charge le pack deja selectionne, donc un
build de test ecrit sous un nouveau nom valide l'ancien code. Le mode `--test` ecrase tous les
`FliflightVanillaPlus-*.zip` presents pour rendre cela impossible.

## Lecons apprises

- **Dans une passe d'ombre, les matrices fixed-function sont celles de l'ombre.** Utiliser
  `gl_ModelViewMatrix` comme si c'etait celle du gbuffer donne une shadowmap incoherente.
- **Verifier le nombre de programmes charges**, pas seulement l'absence d'erreur.
- **Ne jamais generer N fois la meme declaration locale** : sortir la logique dans une fonction.
- **Une macro ne se definit qu'une fois** dans toute la chaine d'include, meme sous `#ifdef`.
- **Toujours verifier le referentiel** (espace vue / espace monde / espace ombre).
- **Un uniform peut valoir 0** : deriver la donnee dans le vertex (`viewDist`, normale monde).
- **Les directives `shaders.properties` pesent plus lourd que le code** (`alphaTest.*`).
- **Une animation liee a la geometrie doit dependre de la position MONDE.**
- **Un script de build ne doit pas reecrire la config silencieusement.**
- **Lire aussi les avertissements, pas seulement les erreurs.**
