# Xray — See Through Terrain (Bedrock)

## Ce que fait ce pack

Il rend transparents les blocs pleins du terrain pour laisser voir ce qui est enterre, et il
laisse deliberement VISIBLES les blocs qui ont de la valeur.

- **355 blocs poses deviennent transparents** (blockstates rediriges) : pierre, deepslate, terre,
  sable, netherrack, end_stone, gravier, argile, feuillages, bois, neige, sculk...
- **21 minerais restent pleins et lumineux** : ils sont dessines en toutes circonstances, y compris
  enterres au fond d'une paroi, et portent une emission lumineuse pour ressortir dans le noir.
- **7 blocs precieux restent visibles** : `spawner`, `trial_spawner`, `vault`, `budding_amethyst`,
  `ancient_debris`, `barrel`, `reinforced_deepslate`.
- Les overlays qui masquent la vue sont neutralises (flou de citrouille, teinte sous l'eau, vignette).

## Comment ca marche

Deux mecanismes, et il a fallu les deux pour que le pack serve a quelque chose.

1. **Le terrain devient une coque.** Chaque bloc plein recoit un modele fait de six dalles de
   0,5 unite, une par face, chacune portant `cullface`. Une face portant `cullface` n'est dessinee
   que si le bloc voisin n'est pas opaque : entre deux blocs de pierre, rien n'est dessine et le
   terrain se reduit a un lisere.
2. **Les blocs a voir ne portent pas de `cullface`.** Un minerai enterre est entoure de blocs
   opaques : ses six faces seraient toutes supprimees et il ne serait jamais dessine. Ils ont donc
   leur propre cube, sans `cullface`, plus une emission lumineuse.

Le pack passe par les **blockstates** et jamais par les modeles de blocs : le modele d'item d'un
bloc pointe sur `models/block/<nom>.json`, donc l'ecraser rendrait le bloc invisible dans
l'inventaire et en main. Seul le bloc pose change.

## Installation

Ouvre le `.mcpack` : le jeu l'importe. Un `.mcpack` depose directement dans le
dossier `resource_packs/` est **ignore** — il faut soit l'ouvrir, soit y poser le dossier extrait.

## Versions

`min_engine_version` 1.21.0. Teste : **non teste sur un appareil Bedrock** — les 356 identifiants
sont en revanche verifies contre la table des blocs du jeu, donc aucun nom invalide ne peut etre
livre. Le rendu reste a confirmer en jeu.

## Ce qui est specifique a cette edition

Bedrock n'a pas de jar a analyser : la liste part des blocs pleins identifies cote Java, et chaque
nom candidat est confronte a la table d'identifiants Bedrock. Les deux editions ont diverge sur les
noms, et deviner ne pardonne pas — un identifiant inconnu produit une erreur de contenu.

- Masques : `blockshape: invisible`, sans toucher aux textures.
- Minerais et blocs precieux lumineux : carte `_mer` 16x16 (R metal, **V emissif**, B rugosite) dont
  le canal emissif est derive de la luminosite de la texture, plus le `.texture_set.json` associe.
- `lighting/global.json` : sans lui, une grotte reste noire et cache tout ce que le pack devoile.

## Limites connues

- `light_gray_glazed_terracotta` n'a pas d'equivalent trouve dans la table.
- Le pack n'affecte que les blocs poses.
- En multijoueur, la plupart des serveurs interdisent ce type de pack.
