# Fliflight Vanilla Plus - shader pack

Pack de shader client **Vanilla+**, profil **Potato**. Version **v0.6**.

- **Cible** : Minecraft Java 1.21.x - OptiFine / Iris
- **Verifie** : OptiFine 1.21.4_HD_U_J4_pre2 - **21 programmes, 0 erreur**
  (19 gbuffers + composite + final)

## Effets actifs

| Effet | Detail |
|---|---|
| **Aucun brouillard** | eau, lave, poudreuse : visibilite totale |
| **Bloom** | seuil + flou H + flou V, **2 passes plein ecran** |
| **Feuillage qui ondule** | herbe, feuilles, fleurs, cultures |
| **Ciel + soleil** | halo solaire + chaleur a l'horizon |
| Etalonnage | saturation +12 %, contraste +5 %, luminosite +2 % |

Desactives : ombres, nettete, brume d'horizon.

## v0.6 : le gros levier de perf etait une DIRECTIVE, pas du code

Le pack ne declaraite **aucune directive `alphaTest`**. Sans elles, OptiFine desactive son
chemin de rendu rapide pour ces programmes et **ne peut pas fusionner l'opaque et le cutout**
(feuillage) : le terrain est rendu en plusieurs passes. C'est le poste le plus lourd d'un pack
de shader, et BSL l'optimise pendant que ce pack le payait plein pot.

```properties
alphaTest.gbuffers_terrain=GREATER 0.1
alphaTest.gbuffers_clouds=GREATER 0.005
alphaTest.gbuffers_hand=GREATER 0.005
alphaTest.gbuffers_water=GREATER 0.001
alphaTest.gbuffers_weather=GREATER 0.0001
```

Le shader n'a **pas** a faire le `discard` : OptiFine s'en charge d'apres ces seuils. C'est
pourquoi BSL ne contient aucun `discard` dans son shader de terrain. Verifie : BSL declare ces
5 lignes, ce pack n'en avait aucune.

Ajoute aussi `shadowEntities=false` et `shadowBlockEntities=false` (sans ombres, inutile de
redessiner les entites).

## Passe plein ecran supprimee

Le flou **vertical** du bloom est desormais fusionne dans `final.fsh` :
`composite` fait le seuil + le flou horizontal, `final` termine le flou vertical et applique
l'etalonnage. **2 passes au lieu de 3**, et 3 lectures de texture en moins par pixel.

## Bilan perf

| | v0.2 | v0.5 | **v0.6** |
|---|---|---|---|
| Passes plein ecran | 6 | 3 | **2** |
| Passe d'ombre | oui | non | **non** |
| **Lectures de texture / pixel** | **51** | 12 | **9** |
| Chemin rapide OptiFine (`alphaTest`) | non | non | **oui** |
| Programmes charges | 26 | 22 | **21** |

## Ce que le pack ne peut PAS expliquer

Avoir **autant de FPS qu'avec BSL** est un resultat anormal : ce pack fait 2 passes plein
ecran la ou BSL en fait une quinzaine. Si les deux donnent le meme resultat, alors le GPU
**n'est pas le facteur limitant** et optimiser davantage le shader ne changera rien.

A verifier cote jeu (F3 ouvert) :

1. **La ligne `GPU:` de F3.** Si elle est basse (< 60-70 %) pendant que les FPS sont bas,
   c'est le **CPU** : distance de rendu, generation de chunks, entites. Reculer la distance de
   rendu de 4 chunks change plus les FPS que n'importe quel reglage de shader.
2. **VSync / limiteur** : Options > Video Settings > VSync OFF, et Max Framerate a 260.
3. **OptiFine** : Video Settings > Performance > *Fast Render* ON, *Smooth FPS* ON,
   *Chunk Updates* sur 1, *Smooth World* ON. Et **Render Quality 1.0**.
4. **Resolution de l'ecran** : le cout d'un shader est proportionnel au nombre de pixels.
   En 1440p ou 4K, 2 passes plein ecran restent cheres sur un GPU faible.
5. **Distance de rendu** : c'est le premier levier, avant le shader pack.

## Reglages (`lib/config.glsl`)

```glsl
#define BLOOM_STRENGTH    0.45   // 0.0 = bloom off  -> teste deja une vraie difference
#define BLOOM_THRESHOLD   0.68
#define BLOOM_SPREAD      2.5
#define WAVE_SCALE        1.00
#define SUN_HALO_STRENGTH 0.55
//#define SHARPEN
//#define HORIZON_HAZE
//#define SHADOWS
```

Mettre `BLOOM_STRENGTH` a 0.0 supprime `composite` : ne reste alors qu'**une seule passe plein
ecran** (`final`). C'est le test le plus rapide pour savoir si le post-traitement est le
facteur limitant.

## Valider, tester, livrer

```bash
python scripts/validate_shader.py shaderpacks/fliflight-vanilla-plus
python scripts/rebuild_shaderzip.py --test
bash scripts/of_compile_test.sh <etiquette>
python scripts/rebuild_shaderzip.py
```

**Toujours controler le NOMBRE de programmes charges** : OptiFine charge le pack deja
selectionne, donc un build de test ecrit sous un nouveau nom valide l'ancien code. Le compte
doit correspondre a ce que le changement implique (supprimer un composite = -1).
