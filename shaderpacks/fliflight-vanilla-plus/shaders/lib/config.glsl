#ifndef CONFIG_GLSL
#define CONFIG_GLSL

// ============ PROFIL ============
// POTATO : par defaut, leger (shadowmap 1024, bloom 5 taps, ombres 64 blocs)
// Decommenter la ligne ci-dessous pour la version lourde.
//#define HIGH_QUALITY

// ============ EFFETS (commenter une ligne pour le desactiver) ============
#define BLOOM
#define SHADOWS
#define WAVES
#define CUSTOM_SKY
#define HORIZON_HAZE

// ============ BLOOM ============
#define BLOOM_STRENGTH   0.45
#define BLOOM_THRESHOLD  0.68
#define BLOOM_SPREAD     2.5    // ecart entre les taps de flou (plus grand = flou plus large)

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

// ============ BRUME D'HORIZON ============
// Remet un fondu vers la couleur du ciel sur le terrain TRES lointain, sans
// remettre le brouillard (eau / lave / poudreuse restent totalement clairs).
#define HORIZON_HAZE_START    0.72   // fraction de la distance de rendu ou ca commence
#define HORIZON_HAZE_STRENGTH 0.85   // 0.0 = desactive, 1.0 = fond complet

#endif
