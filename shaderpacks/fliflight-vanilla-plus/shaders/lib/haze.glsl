#ifndef HAZE_GLSL
#define HAZE_GLSL

#include "/lib/config.glsl"

uniform vec3 cameraPosition;
uniform vec3 skyColor;
uniform float far;

// Fondu du terrain tres lointain vers la couleur du ciel.
// Ce n'est PAS le brouillard du jeu : il ne touche que les derniers 28 % de la
// distance de rendu, donc rien de ce qui est proche, sous l'eau ou dans la lave.
vec3 applyHaze(vec3 color, vec3 worldPos) {
    #ifdef HORIZON_HAZE
    float dist = length(worldPos - cameraPosition);
    float start = far * HORIZON_HAZE_START;
    float t = clamp((dist - start) / max(far - start, 1.0), 0.0, 1.0);
    color = mix(color, skyColor, t * t * HORIZON_HAZE_STRENGTH);
    #endif
    return color;
}

#endif
