#ifndef HAZE_GLSL
#define HAZE_GLSL

#include "/lib/config.glsl"

#ifdef HORIZON_HAZE
uniform vec3 skyColor;
#endif

// `viewDist` vient du vertex shader : en espace vue la camera est a l'origine,
// donc length(viewPos) EST la distance a la camera. Aucune dependance a
// `far` ni `cameraPosition`, qui peuvent valoir 0 selon le contexte.
vec3 applyHaze(vec3 color, float viewDist) {
    #ifdef HORIZON_HAZE
    float t = clamp((viewDist - HAZE_START_BLOCKS) / (HAZE_END_BLOCKS - HAZE_START_BLOCKS), 0.0, 1.0);
    color = mix(color, skyColor, t * t * HAZE_STRENGTH);
    #endif
    return color;
}

#endif
