# Fliflight Vanilla Plus - shader pack

Pack de shader client **Vanilla+** : fidele au style Minecraft, juste plus beau.
Version **v0.4 « Potato »**.

- **Cible** : Minecraft Java 1.21.x - OptiFine / Iris
- **Format** : OptiFine shader pack (`#version 120`, GLSL legacy)
- **Verifie** : OptiFine 1.21.4_HD_U_J4_pre2 - 24 programmes, 0 erreur GLSL,
  dans les **deux** configurations (Potato par defaut, et nettete + brume activees)

## Effets actifs

| Effet | Detail |
|---|---|
| **Aucun brouillard** | eau, lave, poudreuse : visibilite totale |
| **Bloom** | seuil + flou H fusionnes, puis flou V (**2 passes**) |
| **Ombres** | shadowmap 768, portee 56 blocs, biais proportionnel a la pente |
| **Feuillage qui ondule** | herbe, feuilles, fleurs, cultures |
| **Ciel + soleil** | halo solaire + chaleur a l'horizon |
| Etalonnage | saturation +12 %, contraste +5 %, luminosite +2 % |

Nettete et brume d'horizon : **desactivees par defaut**, une ligne a decommenter.

## Corrige en v0.4 : l'ombre aberrante face au soleil

**Cause racine : la normale etait en espace VUE, utilisee comme si elle etait en espace MONDE.**

```glsl
vNormal = normalize(gl_NormalMatrix * gl_Normal);   // gl_NormalMatrix -> espace VUE
...
vec3 sp = ToShadow(worldPos + vNormal * 0.06);      // vecteur vue ajoute a une position monde
```

Le decalage anti-acne partait donc dans une direction qui **change avec l'orientation de la
camera** : l'artefact apparaissait ou disparaissait selon ou l'on regardait, typiquement face
au soleil. Correction :

```glsl
vNormal = normalize(mat3(gbufferModelViewInverse) * (gl_NormalMatrix * gl_Normal));
```

**Meme famille d'erreur que la v0.3.1** (uniform valant 0 sans qu'on le sache) : une donnee
utilisee dans le mauvais referentiel. Le symptome dependait du regard, ce qui est la signature
d'un vecteur d'espace vue.

**Deuxieme manque : aucun biais proportionnel a la pente.** Un biais constant est minuscule en
angle rasant, or « regarder le soleil » = surfaces eclairees en rasant. Ajoute, sur le modele
de BSL :

```glsl
float NoL = dot(normal, sunDir);
float biasFactor = sqrt(1.0 - NoL * NoL) / max(NoL, 0.05);   // tan de l'angle = explose en rasant
float nOffset = min(SHADOW_NORMAL_OFF * (1.0 + biasFactor * 0.4), SHADOW_NORMAL_MAX);
```

- decalage le long de la normale **en blocs** (previsible, borne pour eviter le peter-panning),
- biais de profondeur lui aussi proportionnel a la pente,
- **early-out** quand `NoL <= 0` (face opposee au soleil : sombre, aucune lecture)
  et quand `skyFactor ≈ 0` (interieur / souterrain : pas d'ombre solaire, aucune lecture).

## Perf : v0.2 -> v0.4

| | v0.2 | v0.3 | **v0.4** |
|---|---|---|---|
| Passes de bloom | 5 | 3 | **2** |
| **Lectures de texture / pixel (bloom + final)** | **51** | 17 | **12** |
| Resolution shadowmap | 2048 | 1024 | **768** |
| Portee des ombres | 128 blocs | 64 | **56** |
| Nettete (4 lectures) | toujours | toujours | **opt-in** |
| Lecture d'ombre si face a l'ombre | oui | non | **non** |
| Lecture d'ombre en interieur | oui | oui | **non** |
| Fondu de sortie d'ombre | non | oui | oui |

Le seuil de luminance est desormais applique **pendant** le flou horizontal : le bright-pass
et le flou H ne font plus qu'une passe, ce qui supprime une passe plein ecran entiere.

Pour la qualite v0.2 : decommenter `#define HIGH_QUALITY` dans `lib/config.glsl`.

## Reglages (`lib/config.glsl`)

```glsl
#define BLOOM_STRENGTH    0.45   // 0.0 = bloom off
#define SHADOW_STRENGTH   0.85   // 0.0 = ombres off
#define SHADOW_DISTANCE   56.0   // blocs
#define SHADOW_BIAS_SLOPE 0.25   // anti-acne en angle rasant
#define SHADOW_NORMAL_OFF 0.15   // decalage le long de la normale (blocs)
//#define SHARPEN                // decommenter : nettete (+4 lectures / pixel)
//#define HORIZON_HAZE           // decommenter : brume d'horizon
```

## Chainage des buffers

```
gbuffers   -> colortex0   (scene)
composite  -> colortex1   (seuil + flou H)     /*DRAWBUFFERS:1*/
composite1 -> colortex2   (flou V)             /*DRAWBUFFERS:2*/
final      -> ecran       (colortex0 + colortex2)
```

## Valider et tester avant de livrer

```bash
python scripts/validate_shader.py shaderpacks/fliflight-vanilla-plus
python scripts/rebuild_shaderzip.py --test
bash scripts/of_compile_test.sh <etiquette>
```

Le validateur attrape les erreurs a ecran noir silencieux : `#include` sans extension,
`DRAWBUFFERS` manquant, litteraux flottants malformes, varyings absents du vertex,
uniformes declares en double (error C1038), sampler d'ombre mal nomme.
Il ignore les commentaires dans ses comptages (sinon `// 1)` declenche un faux positif).

Le test de compilation lance OptiFine en launchwrapper et lit `logs/latest.log` :
`Program loaded:` par programme et `Error compiling fragment shader:` + numero de ligne en cas
d'echec. **Toujours tester chaque combinaison de `#define`**, pas seulement le defaut.

## Lecons apprises (a ne pas refaire)

- **Toujours verifier le referentiel.** `gl_NormalMatrix` = espace vue ; `gbufferModelViewInverse`
  = vue vers monde. Melanger les deux donne un bug dependant de l'orientation de la camera.
- **Un uniform peut valoir 0** : ne jamais faire reposer un seuil visuel sur sa valeur.
  Preferer une donnee calculee dans le vertex (`viewDist`, normale monde).
- **Un biais d'ombre constant ne suffit pas** : il faut un terme proportionnel a la pente.
- **Un effet invisible pour l'auteur ne se livre pas actif.**
- **Borne tout decalage** (peter-panning) et **sors tot** de ce qui ne sert a rien.

## Roadmap

- v0.5 : ombres filtrees (PCF) en option, eau avec vagues, ciel etoile
