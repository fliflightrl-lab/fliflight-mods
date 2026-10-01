# Fliflight Vanilla Plus - shader pack

Pack de shader client **Vanilla+**, profil **Potato**. Version **v0.9**.

- **Cible** : Minecraft Java 1.21.x - OptiFine / Iris
- **Verifie** : OptiFine 1.21.4_HD_U_J4_pre2 - **21 programmes, 0 erreur, 0 avertissement**

## Reglages dans le jeu

Tout se regle dans **Options -> Video Settings -> Shader Options**, sans toucher au GLSL :

- **Ecran principal** : profils, feuillage, bloom, brume d'horizon, nettete
- **Sous-ecran LIGHT** : lumiere teintee, lumiere directionnelle, eclairage par face, couleurs des torches et du ciel
- **Sous-ecran WATER** : houle, reflet du soleil, teinte sous l'eau
- **Sous-ecran SKY** : ciel, halos, etoiles, aube/crepuscule, tone mapping

Trois **profils** : `POTATO`, `BALANCED`, `QUALITY` (mêmes options, valeurs différentes).

**`SHADOWS` est volontairement absent de l'ecran.** Le programme d'ombre n'est pas embarque dans
ce pack : l'activer donnerait des ombres cassees. La doc OptiFine prevoit un joker `*` qui affiche
« tout le reste » — il n'est **pas** utilise, precisement pour que cette option reste inaccessible.

## Effets

| Effet | Detail | Cout |
|---|---|---|
| **Aucun brouillard** | eau, lave, poudreuse : visibilite totale | - |
| **Bloom** | seuil + flou H dans `composite` (demi-resolution), flou V dans `final` | 2 passes |
| **Feuillage qui ondule** | herbe, feuilles, fleurs, cultures | vertex |
| **Eau animee** | houle sur la face du dessus, ancree en position monde | vertex |
| **Reflet sur l'eau** | normale ondulee par deux sinus croises, reflet du soleil | eau seulement |
| **Teinte sous l'eau** | leger decalage quand la camera est immergee | 0 |
| **Lumiere teintee** | torches chaudes, ciel froid | 0 lecture |
| **Lumiere directionnelle** | le cote expose au soleil prend la couleur de l'heure | 0 |
| **Eclairage par face** | le lightmap ne varie pas selon la face : ajoute ici | 0 |
| **Tone mapping** | rolloff des hautes lumieres au lieu du clamp | 0 |
| **Sombrage des nuages** | les nuages suivent l'heure | 0 |
| **Ciel** | halos solaire et lunaire, bande d'aube, etoiles | ciel |
| **Brume d'horizon** | refond le terrain tres lointain vers le ciel | 0 |
| **Etalonnage par heure** | nuits froides, aube et crepuscule chauds | 0 |

## v0.9 - ce qui a ete ajoute

**Eclairage par orientation de face.** Le lightmap de Minecraft ne varie pas selon l'orientation :
toutes les faces d'un bloc recoivent exactement la meme lumiere, ce qui rend le monde plat. On
module ici par `vNormal.y` et par l'orientation face au soleil :

```glsl
float faceLight = 1.0 + (topness - 0.5) * FACE_TOP_CONTRAST
                      + (sunFace - 0.5) * FACE_SUN_CONTRAST;
light *= mix(1.0, faceLight, skyAmt * FACE_LIGHT_STRENGTH);
```

C'est le remplacant le plus efficace des ombres : **gain de profondeur percu important, zero
lecture de texture, zero passe, zero branchement.**

**Tone mapping.** Au-dessus d'un genou (`TONE_KNEE`), les hautes lumieres sont compressees vers 1.0
au lieu d'etre clampees : le bloom garde son detail au lieu de devenir un aplat blanc.

**Reflet sur l'eau + teinte sous l'eau.** La normale est perturbee par deux sinus croises sur la
position monde, puis un Blinn-Phong donne le reflet du soleil. `isWater` vient du vertex shader,
donc le calcul ne s'execute que sur les fragments d'eau.

**Sombrage des nuages.** Modulation autour de 1.0 (et non assombrissement) : les nuages suivent
l'heure sans que la nuit les rende noirs deux fois.

## Reglages exposes

Les teintes sont decoupees en composantes **numeriques** (`BLOCK_TINT_R`, `BLOCK_TINT_G`, ...)
et non en `vec3(...)` : une valeur non numerique n'est pas un reglage valide pour OptiFine. On peut
donc regler la couleur de la lumiere **en direct dans le menu**.

Idem : `SHADOW_FADE_START` (une expression) a ete supprime et calcule inline dans le shader —
OptiFine ne sait pas exposer une expression comme option.

## STATUT DES OMBRES : non livrees

Trois tentatives, trois artefacts differents signales en jeu. La cause racine de la v0.8 etait
reelle et **prouvee** (dans une passe d'ombre `gl_ModelViewMatrix` est la matrice d'OMBRE, donc
`gbufferModelViewInverse` dessus donne une position monde absurde et la shadowmap se remplit de
geometrie placee n'importe ou), mais le symptome suivant - ombres buggees dans un perimetre autour
du joueur et clignotantes - n'est pas explique.

Pistes restantes, non testees :

- **Distorsion non uniforme de `shadowProjection`**, centree sur le joueur. BSL la compense des
  deux cotes (`DistortShadow` au fragment, son inverse au vertex). Ce pack n'applique rien.
  C'est exactement la zone (autour du joueur) ou un ecart serait maximal.
- **`shadowFade`**, uniform OptiFine qui passe a 0 quand les ombres doivent s'effacer (nuit,
  pluie, limite de distance). Ignore ici - piste directe pour un clignotement.

## Corriges au fil des versions

- **`invalid program "composite"` / ecran blanc** : cinq declarations locales identiques dans la
  meme portee. GLSL 1.20 interdit de redeclarer un nom -> logique deplacee dans une fonction.
- **`error C1038: declaration of "cameraPosition" conflicts`** : uniform declare dans un lib et
  dans le fichier qui l'inclut.
- **`#include` sans extension** : OptiFine exige le nom complet, sinon ecran noir silencieux.
- **`Ambiguous shader option`** : une macro definie deux fois. La doc OptiFine confirme que
  l'option est alors **desactivee et non modifiable**.
- **Ecran bleu** : brume calculee depuis `far`, qui n'est pas la distance de rendu.
- **Voile noir au loin** : sampler d'ombre nomme `tex` au lieu de `texture`.
- **Ombres dependantes de la camera** : `gl_NormalMatrix` est en espace VUE.
- **`Block not found for name: minecraft:grass`** : renomme `short_grass` en 1.20.3.

## Perf

| | v0.2 | v0.6 | v0.8.1 | **v0.9** |
|---|---|---|---|---|
| Passes plein ecran | 6 | 2 | 2 | **2** |
| **Lectures de texture / pixel** | **51** | 9 | 9 | **9** |
| Pixels ecrits pour le bloom | plein ecran | plein ecran | 1/4 | **1/4** |
| Chemin rapide OptiFine (`alphaTest`) | non | oui | oui | **oui** |
| Passe d'ombre | oui | non | non | **non** |
| Programmes charges | 26 | 21 | 21 | **21** |

v0.9 ajoute **cinq effets** sans ajouter une seule passe ni une seule lecture de texture.

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
- **Un reglage OptiFine doit etre numerique ou booleen.** `vec3(...)` n'est pas exposable ;
  une expression non plus.
- **Sans le joker `*`, `screen=` masque tout ce qui n'est pas liste** : c'est ainsi qu'on cache
  une option dangereuse.
- **Lire les avertissements d'OptiFine**, pas seulement les erreurs.
- **Controler le nombre de programmes charges**, pas seulement l'absence d'erreur.
- **Un script de build ne doit pas reecrire la config silencieusement.**
- **Une macro ne se definit qu'une fois** dans toute la chaine d'include.
- **Verifier le referentiel** (espace vue / monde / ombre).
- **Un uniform peut valoir 0** : deriver la donnee dans le vertex.
- **Les directives `shaders.properties` pesent plus lourd que le code** (`alphaTest.*`).
- **Une animation liee a la geometrie doit dependre de la position MONDE.**
- **Un effet qu'on ne peut pas observer ne se livre pas actif.**
