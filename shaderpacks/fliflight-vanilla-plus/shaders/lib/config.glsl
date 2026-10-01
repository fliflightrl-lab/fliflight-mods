#ifndef CONFIG_GLSL
#define CONFIG_GLSL

// ============ PROFIL ============
//#define HIGH_QUALITY

// ============ EFFETS (commenter une ligne pour le desactiver) ============
#define BLOOM
#define WAVES
#define CUSTOM_SKY
#define WATER_WAVES
#define STARS
#define LIGHT_TINT
#define DIRECTIONAL_LIGHT
#define TIME_GRADE

//#define SHARPEN
//#define HORIZON_HAZE
//#define SHADOWS

// ============ BLOOM ============
#define BLOOM_STRENGTH   0.45
#define BLOOM_THRESHOLD  0.68
#define BLOOM_SPREAD     2.5

// ============ LUMIERE (A) ============
// Torches chaudes, ciel froid. Les deux teintes ont une luminance ~1.0 : teinter
// ne change donc pas la luminosite globale, seulement la couleur.
#define LIGHT_TINT_STRENGTH 0.65
#define BLOCK_TINT vec3(1.18, 0.98, 0.76)
#define SKY_TINT   vec3(0.91, 1.00, 1.24)
// Teinte directionnelle : le cote expose au soleil prend la couleur de l'heure.
#define DIRECTIONAL_STRENGTH 0.35

// ============ EAU (B) ============
// Deplacement de sommets. Fonction de la POSITION MONDE : la houle est donc
// continue d'un chunk a l'autre, aucune couture visible.
#define WATER_WAVE_HEIGHT 0.10
#define WATER_WAVE_SPEED  1.15

// ============ CIEL (C) ============
#define STARS_STRENGTH     0.85
#define MOON_HALO_STRENGTH 0.35
#define DUSK_STRENGTH      0.45

// ============ OMBRES ============
#ifdef HIGH_QUALITY
  #define SHADOW_DISTANCE 128.0
#else
  #define SHADOW_DISTANCE 56.0
#endif
#define SHADOW_MAP_RES   768.0
#define SHADOW_STRENGTH  0.85
#define SHADOW_FADE_START (SHADOW_DISTANCE * 0.70)
#define SHADOW_BIAS_SLOPE  0.25
#define SHADOW_BIAS_DIST   0.004
#define SHADOW_BIAS_MIN    1.0
#define SHADOW_NORMAL_OFF  0.15
#define SHADOW_NORMAL_MAX  0.60

// ============ FEUILLAGE ============
#define WAVE_SCALE 1.00

// ============ CIEL (halo solaire) ============
#define SUN_HALO_STRENGTH 0.55

// ============ BRUME D'HORIZON ============
#define HAZE_START_BLOCKS 120.0
#define HAZE_END_BLOCKS   300.0
#define HAZE_STRENGTH     0.85

#endif
