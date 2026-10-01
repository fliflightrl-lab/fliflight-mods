#ifndef CONFIG_GLSL
#define CONFIG_GLSL

// ============ PROFIL ============
//#define HIGH_QUALITY

// ============ EFFETS (commenter une ligne pour le desactiver) ============
#define BLOOM
#define SHADOWS
#define WAVES
#define CUSTOM_SKY

// Nettete : 4 lectures de texture en plus par pixel. Desactive en Potato.
//#define SHARPEN

// Brume d'horizon : DESACTIVEE par defaut.
//#define HORIZON_HAZE

// ============ BLOOM ============
#define BLOOM_STRENGTH   0.45
#define BLOOM_THRESHOLD  0.68
#define BLOOM_SPREAD     2.5

// ============ OMBRES ============
#ifdef HIGH_QUALITY
  #define SHADOW_DISTANCE  128.0
#else
  #define SHADOW_DISTANCE  56.0
#endif
#define SHADOW_MAP_RES   768.0    // DOIT correspondre a shaders.properties
#define SHADOW_STRENGTH  0.85
#define SHADOW_FADE_START (SHADOW_DISTANCE * 0.70)

// Biais. Le terme de pente (biasFactor = tan de l'angle normal/soleil) explose
// en angle rasant : c'est exactement le cas "face au soleil".
#define SHADOW_BIAS_SLOPE  0.25   // multiplicateur du terme de pente
#define SHADOW_BIAS_DIST   0.004  // terme de distance (par bloc)
#define SHADOW_BIAS_MIN    1.0    // plancher, en unites de resolution
#define SHADOW_NORMAL_OFF  0.15   // decalage le long de la normale (blocs)
#define SHADOW_NORMAL_MAX  0.60   // plafond du decalage (anti peter-panning)

// ============ FEUILLAGE ============
#define WAVE_SCALE        1.00

// ============ CIEL ============
#define SUN_HALO_STRENGTH 0.55

// ============ BRUME D'HORIZON (seuils en blocs) ============
#define HAZE_START_BLOCKS 120.0
#define HAZE_END_BLOCKS   300.0
#define HAZE_STRENGTH     0.85

#endif
