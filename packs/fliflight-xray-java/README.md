# Xray — See Through Terrain (Java)

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

Place le `.zip` dans `.minecraft/resourcepacks/` puis active-le dans
**Options → Packs de ressources**. En jeu, `F3+T` recharge les ressources sans relancer.

## Versions

`pack_format` 46, donc accepte automatiquement a partir de **1.21.4**. La plage declaree descend
plus bas car la mecanique (blockstates + coques) ne depend pas de la version, mais **seule 1.21.4 a
ete testee** : sous 1.21.2, l'emission lumineuse n'existe pas et les minerais resteront visibles
sans halo. Non verifie sous 1.21.4.

## Limites connues

- Le pack n'affecte que les blocs **poses** ; un bloc tenu ou en inventaire reste normal.
- Sans `light_emission`, un minerai dans une grotte non eclairee sera visible mais sombre.
- En multijoueur, la plupart des serveurs interdisent ce type de pack : a verifier avant usage.

## Reconstruction

```bash
python scripts/build_xray.py
```

Le script lit le jar du jeu (`build/client-1.21.4.jar`) pour enumerer les blocs pleins, et refuse
de livrer si un modele de bloc vanilla est ecrase, si un gabarit abstrait apparait, si un bloc
precieux se retrouve masque, ou si un bloc attendu n'a pas de blockstate.
