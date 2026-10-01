# Fliflight Vanilla Plus - shader pack

Pack de shader client **Vanilla+**, profil **Potato**. Version **v0.8.1**.

- **Cible** : Minecraft Java 1.21.x - OptiFine / Iris
- **Verifie** : OptiFine 1.21.4_HD_U_J4_pre2 - **21 programmes, 0 erreur, 0 avertissement**

## Effets actifs

| Effet | Detail |
|---|---|
| **Aucun brouillard** | eau, lave, poudreuse |
| **Bloom** | seuil + flou H dans `composite` (demi-resolution), flou V dans `final` |
| **Feuillage qui ondule** | herbe, feuilles, fleurs, cultures |
| **Eau animee** | houle sur la face du dessus, ancree en position monde |
| **Lumiere teintee** | torches chaudes, ciel froid, sans lecture de texture en plus |
| **Lumiere directionnelle** | le cote expose au soleil prend la couleur de l'heure |
| **Ciel** | halo solaire et lunaire, bande chaude a l'aube, etoiles |
| **Brume d'horizon** | refond le terrain tres lointain vers la couleur du ciel |
| **Etalonnage par heure** | nuits froides, aube et crepuscule chauds |

Desactives (un `#define` a decommenter) : `SHADOWS`, `SHARPEN`.

## STATUT DES OMBRES : non livrees, et pourquoi

**Les ombres ne sont pas resolues. Elles sont desactivees, et le programme d'ombre n'est meme
pas embarque dans le zip** (donc OptiFine ne fait aucune passe d'ombre).

Trois tentatives, trois artefacts differents signales en jeu :

1. **v0.3** - un voile sombre au loin, dependant de l'angle de vue. Deux bugs reels corriges :
   sampler d'ombre nomme `tex` au lieu de `texture` (shadowmap vide -> tout a l'ombre), et
   `vNormal` en espace vue utilise dans des calculs en espace monde.
2. **v0.4** - artefact toujours present, dependant de l'orientation de la camera. Ajout du biais
   proportionnel a la pente (`sqrt(1-NoL^2)/NoL`). Insuffisant.
3. **v0.8** - cause racine corrigee et **prouvee** : dans une passe d'ombre, `gl_ModelViewMatrix`
   est la matrice d'OMBRE, pas celle du gbuffer. La ligne `gbufferModelViewInverse * (gl_ModelViewMatrix
   * gl_Vertex)` produisait donc une position monde absurde et la shadowmap etait remplie de
   geometrie placee n'importe ou. Preuve : BSL doit inverser **deux** matrices
   (`shadowModelViewInverse * shadowProjectionInverse * ftransform()`) pour retrouver l'espace
   monde. Correction appliquee : `shadowModelViewInverse * (gl_ModelViewMatrix * gl_Vertex)`.
   **Resultat en jeu : ombres buggees dans un perimetre autour du joueur, et clignotantes.**

Ce dernier symptome (perimetre + scintillement) n'est pas encore explique. Les pistes restantes,
non testees :

- **distorsion de la shadowmap d'OptiFine** : `shadowProjection` integre une compression
  non uniforme centree sur le joueur. BSL applique `DistortShadow` cote fragment et l'inverse
  cote vertex. Ce pack n'applique rien - ce qui devrait etre auto-coherent, mais c'est
  precisement la zone (autour du joueur) ou l'ecart serait maximal.
- **`shadowFade`** : uniform OptiFine signalant que les ombres doivent s'effacer (nuit, pluie,
  limite de distance). Ce pack l'ignore, donc ses ombres ne s'effacent pas quand OptiFine
  l'attend - piste directe pour un scintillement.
- **biais encore insuffisant** en angle rasant malgre le terme de pente.

**Decision** : ne plus livrer d'ombre tant que le symptome n'est pas compris. Le pack est
utilisable et rapide sans. La lumiere directionnelle (voir plus bas) restitue une partie de
l'interet visuel des ombres, sans passe d'ombre.

**Pour reprendre le chantier, il faut une information que l'auteur ne peut pas obtenir seul** :
une description precise de l'artefact (rayures / moiré ? carres ? formes incoherentes ?),
ou une capture d'ecran analysable. Une visualisation de debogage peut etre ajoutee si besoin.

## Corriges au fil des versions

- **`invalid program "composite"` / ecran blanc** : `composite.fsh` declaraite `vec3 s` et
  `float l` cinq fois dans la meme portee. GLSL 1.20 interdit de redeclarer un nom dans une
  portee -> logique deplacee dans une fonction `bright(uv)`.
- **`error C1038: declaration of "cameraPosition" conflicts`** : uniform declare dans un lib
  **et** dans le fichier qui l'inclut. Un uniform ne se declare qu'une fois par chaine.
- **`#include` sans extension** : OptiFine exige le nom complet (`/lib/fs_lit.glsl`), sinon
  ecran noir silencieux.
- **`Ambiguous shader option: SHADOW_DISTANCE`** : macro definie deux fois sous
  `#ifdef HIGH_QUALITY`. Une macro ne se definit qu'une fois.
- **`Block not found for name: minecraft:grass`** : renomme `short_grass` en 1.20.3.
- **Brouillard** : ce n'est pas une texture mais un shader. Un resource pack ne peut pas le changer.
- **Voile sombre a l'horizon** : la brume du jeu lavait le terrain lointain vers le ciel ;
  supprimee sans remplacement, le sol lointain reste sombre. La brume d'horizon (seuils en blocs)
  corrige cela sans remettre le brouillard.

## Perf

| | v0.2 | v0.6 | **v0.8.1** |
|---|---|---|---|
| Passes plein ecran | 6 | 2 | **2** |
| **Lectures de texture / pixel** | **51** | 9 | **9** |
| Pixels ecrits pour le bloom | plein ecran | plein ecran | **1/4** |
| Chemin rapide OptiFine (`alphaTest`) | non | oui | **oui** |
| Passe d'ombre | oui | non | **non** |
| Programmes charges | 26 | 21 | **21** |

## Reglages (`lib/config.glsl`)

```glsl
#define BLOOM_STRENGTH      0.45
#define LIGHT_TINT_STRENGTH 0.65   // 0.0 = couleurs vanilla
#define BLOCK_TINT vec3(1.18, 0.98, 0.76)
#define SKY_TINT   vec3(0.91, 1.00, 1.24)
#define DIRECTIONAL_STRENGTH 0.35
#define WATER_WAVE_HEIGHT   0.10
#define WATER_WAVE_SPEED    1.15
#define STARS_STRENGTH      0.85
#define DUSK_STRENGTH       0.45
#define HAZE_START_BLOCKS   120.0
#define HAZE_END_BLOCKS     300.0
```

Chaque effet se coupe en commentant son `#define`.

## Valider, tester, livrer

```bash
python scripts/validate_shader.py shaderpacks/fliflight-vanilla-plus
python scripts/rebuild_shaderzip.py --test [--shadows|--no-shadows] [--haze|--no-haze]
bash scripts/of_compile_test.sh <etiquette>
python scripts/rebuild_shaderzip.py
sha256sum dist/shaderpacks/*.zip .minecraft/shaderpacks/*.zip
grep -aE "Ambiguous|Block not found|Error compiling|error C[0-9]" <log>
```

**Controler le NOMBRE de programmes charges** : OptiFine charge le pack deja selectionne, donc un
build ecrit sous un nouveau nom valide l'ancien code. `--test` ecrase tous les
`FliflightVanillaPlus-*.zip` presents pour rendre cela impossible.

## Lecons apprises

- **Dans une passe d'ombre, les matrices fixed-function sont celles de l'ombre.**
- **Lire les avertissements d'OptiFine, pas seulement les erreurs** (`Ambiguous`, `Block not found`
  revelent de vrais bugs).
- **Controler le nombre de programmes charges**, pas seulement l'absence d'erreur.
- **Un script de build ne doit pas reecrire la config silencieusement.**
- **Ne jamais generer N fois la meme declaration locale** : utiliser une fonction.
- **Une macro ne se definit qu'une fois** dans toute la chaine d'include.
- **Verifier le referentiel** (espace vue / monde / ombre).
- **Un uniform peut valoir 0** : deriver la donnee dans le vertex (`viewDist`, normale monde).
- **Les directives `shaders.properties` pesent plus lourd que le code** (`alphaTest.*`).
- **Une animation liee a la geometrie doit dependre de la position MONDE.**
- **Un effet qu'on ne peut pas observer ne se livre pas actif.** Pour les ombres, trois cycles
  de test utilisateur pour zero resultat : la bonne reponse etait de desactiver apres le deuxieme.
