# Fliflight Vanilla Plus - shader pack

Pack de shader client **Vanilla+**, profil **Potato** : leger d'abord.
Version **v0.5**.

- **Cible** : Minecraft Java 1.21.x - OptiFine / Iris
- **Format** : OptiFine shader pack (`#version 120`, GLSL legacy)
- **Verifie** : OptiFine 1.21.4_HD_U_J4_pre2
  - config livree : **22 programmes, 0 erreur**
  - config complete (ombres + nettete + brume) : **23 programmes, 0 erreur**

## Effets

| Effet | Etat | Detail |
|---|---|---|
| **Aucun brouillard** | actif | eau, lave, poudreuse : visibilite totale |
| **Bloom** | actif | seuil + flou H en une passe, puis flou V (2 passes) |
| **Feuillage qui ondule** | actif | herbe, feuilles, fleurs, cultures |
| **Ciel + soleil** | actif | halo solaire + chaleur a l'horizon |
| Etalonnage | actif | saturation +12 %, contraste +5 %, luminosite +2 % |
| **Ombres** | **desactivees** | voir ci-dessous |
| Nettete | desactivee | `#define SHARPEN` |
| Brume d'horizon | desactivee | `#define HORIZON_HAZE` |

## Corrige en v0.5 : l'ecran tout blanc

`composite.fsh` declarait `vec3 s` et `float l` **cinq fois dans la meme portee** (une fois par
tap du flou). En GLSL 1.20, redeclarer un nom dans la meme portee est une **erreur de
compilation** :

```glsl
vec3 s = texture2D(...).rgb;   // tap 1
float l = dot(s, ...);
...
vec3 s = texture2D(...).rgb;   // tap 2 -> redeclaration -> "invalid program composite"
```

`composite` etait donc invalide, `colortex1` contenait n'importe quoi, et `final` y ajoutait
ce contenu : **tout devenait blanc**. Corrige en sortant le calcul dans une fonction :

```glsl
vec3 bright(vec2 uv) {
    vec3 c = texture2D(colortex0, uv).rgb;
    float lum = dot(c, vec3(0.2126, 0.7152, 0.0722));
    return c * (max(lum - BLOOM_THRESHOLD, 0.0) / max(lum, 0.0001));
}
```

## Pourquoi mon test offline l'avait manque

Le build de test ecrivait `ZZ-TEST.zip`, alors qu'**OptiFine charge le nom de pack deja
selectionne**, pas le dernier fichier depose. Mes tests validaient donc l'ancien code.

Indice que j'aurais du voir : **le nombre de programmes charges**. J'ai lu « 24 programmes »
alors que la v0.4 n'en a que 23. Le compte etait la preuve que le mauvais pack etait charge.

Corrige : en mode test, le build ecrase **tous** les `FliflightVanillaPlus-*.zip` presents,
donc le pack charge est forcement le nouveau. **Toujours verifier le nombre de programmes
attendu, pas seulement l'absence d'erreur.**

## Ombres : desactivees, et pourquoi

L'artefact sombre face au soleil n'est pas resolu. Deux corrections correctes ont ete
appliquees mais n'ont pas suffi :

1. `vNormal` etait en **espace vue** (`gl_NormalMatrix`) et servait a decaler une position
   **monde** -> le decalage partait dans une direction dependant de la camera. Corrige en
   `mat3(gbufferModelViewInverse) * (gl_NormalMatrix * gl_Normal)`.
2. Aucun biais proportionnel a la pente : ajout de `biasFactor = sqrt(1-NoL^2)/NoL`.

Plutot que de livrer une combinaison cassee, les ombres sont **desactivees** et le
**programme d'ombre n'est meme pas embarque dans le zip** : OptiFine ne fait alors
**aucune passe d'ombre**, ce qui est le gain de perf le plus important du pack.

Pour tester les ombres : `python scripts/rebuild_shaderzip.py --shadows` (compile en 23
programmes, 0 erreur) puis activer le pack.

## Perf

| | v0.2 | v0.3 | v0.4 | **v0.5** |
|---|---|---|---|---|
| Passe d'ombre | oui | oui | oui | **aucune** |
| Passes de bloom | 5 | 3 | 2 | **2** |
| **Lectures de texture / pixel** | **51** | 17 | 12 | **12** |
| Resolution shadowmap | 2048 | 1024 | 768 | — |
| Nettete | toujours | toujours | opt-in | **opt-in** |

Sans passe d'ombre, le monde n'est plus dessine deux fois : c'est le poste le plus lourd
d'un pack de shader.

## Reglages (`lib/config.glsl`)

```glsl
#define BLOOM_STRENGTH    0.45   // 0.0 = bloom off
#define BLOOM_THRESHOLD   0.68   // plus bas = plus d'elements qui bavent
#define BLOOM_SPREAD      2.5    // largeur du flou
#define WAVE_SCALE        1.00
#define SUN_HALO_STRENGTH 0.55
//#define SHARPEN                // +4 lectures / pixel
//#define HORIZON_HAZE
//#define SHADOWS                // cf. ci-dessus
```

## Valider, tester, livrer

```bash
python scripts/validate_shader.py shaderpacks/fliflight-vanilla-plus   # statique
python scripts/rebuild_shaderzip.py --test                            # build de test
bash scripts/of_compile_test.sh <etiquette>                           # compilation reelle
python scripts/rebuild_shaderzip.py                                   # livraison
```

Le validateur attrape les erreurs a effet spectaculaire et sans message clair :
`#include` sans extension, `DRAWBUFFERS` manquant, litteraux flottants malformes,
varyings absents du vertex, uniformes declares en double (error C1038), sampler d'ombre
mal nomme, et **variables locales redeclarees dans la meme portee**.

## Lecons apprises

- **Verifier le nombre de programmes charges**, pas seulement l'absence d'erreur : un test
  peut valider un pack different de celui qu'on croit.
- **Ne jamais generer N fois la meme declaration locale** : sortir la logique dans une fonction.
- **Toujours verifier le referentiel** (espace vue / espace monde).
- **Un uniform peut valoir 0** : deriver la donnee dans le vertex (`viewDist`, normale monde).
- **Un biais d'ombre constant ne suffit pas** : terme proportionnel a la pente.
- **Un effet invisible pour l'auteur ne se livre pas actif.**
- **Une combinaison cassee ne se livre pas** : on retire l'effet et on le rouvre separement.
