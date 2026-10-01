#ifndef CONFIG_GLSL
#define CONFIG_GLSL

// ============ PROFIL ============
// POTATO : par defaut, leger (shadowmap 1024, bloom 5 taps, ombres 64 blocs)
//#define HIGH_QUALITY

// ============ EFFETS (commenter une ligne pour le desactiver) ============
#define BLOOM
#define SHADOWS
#define WAVES
#define CUSTOM_SKY

// Brume d'horizon : DESACTIVEE par defaut. Decommenter pour l'activer.
// Elle refond le terrain tres lointain vers la couleur du ciel (anti "bande sombre").
//#define HORIZON_HAZE

// ============ BLOOM ============
#define BLOOM_STRENGTH   0.45
#define BLOOM_THRESHOLD  0.68
#define BLOOM_SPREAD     2.5

// ============ OMBRES ============
#ifdef HIGH_QUALITY
  #define SHADOW_DISTANCE  128.0
#else
  #define SHADOW_DISTANCE  64.0
#endif
#define SHADOW_STRENGTH   0.85
#define SHADOW_BIAS       0.0012
#define SHADOW_FADE_START (SHADOW_DISTANCE * 0.70)

// ============ FEUILLAGE ============
#define WAVE_SCALE        1.00

// ============ CIEL ============
#define SUN_HALO_STRENGTH 0.55

// ============ BRUME D'HORIZON (seuils en BLOCS, pas de dependance a `far`) ============
#define HAZE_START_BLOCKS 120.0   // distance a laquelle la brume commence
#define HAZE_END_BLOCKS   300.0   // distance a laquelle elle est a fond
#define HAZE_STRENGTH     0.85

#endif
