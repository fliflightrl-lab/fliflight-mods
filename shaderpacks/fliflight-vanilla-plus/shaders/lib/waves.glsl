#ifndef WAVES_GLSL
#define WAVES_GLSL

#include "/lib/config.glsl"

uniform float frameTimeCounter;

attribute vec4 mc_Entity;
attribute vec4 mc_midTexCoord;

float wnoise(vec2 p) {
    return fract(sin(dot(p, vec2(12.9898, 4.1414))) * 43758.5453);
}

float noise2D(vec2 p) {
    vec2 f = floor(p);
    vec2 r = fract(p);
    r = r * r * (3.0 - 2.0 * r);
    float n00 = wnoise(f);
    float n01 = wnoise(f + vec2(0.0, 1.0));
    float n10 = wnoise(f + vec2(1.0, 0.0));
    float n11 = wnoise(f + vec2(1.0, 1.0));
    return mix(mix(n00, n01, r.y), mix(n10, n11, r.y), r.x) - 0.5;
}

vec3 calcMove(vec3 pos, float density, float speed, vec2 mult) {
    pos = pos * density + frameTimeCounter * speed;
    vec3 wave = vec3(noise2D(pos.yz), noise2D(pos.xz + 0.333), noise2D(pos.xy + 0.667));
    return wave * vec3(mult, mult.x);
}

vec3 WavingBlocks(vec3 worldPos, float istopv) {
    vec3 wave = vec3(0.0);
    float id = mc_Entity.x;

    #ifdef WAVES
    if (id == 10100 && istopv > 0.5)
        wave = calcMove(worldPos, 0.35, 1.00, vec2(0.35, 0.08)) * WAVE_SCALE;      // herbe / fougere
    else if (id == 10101)
        wave = calcMove(worldPos, 0.25, 0.80, vec2(0.10, 0.10)) * WAVE_SCALE;      // feuilles
    else if (id == 10102 && istopv > 0.5)
        wave = calcMove(worldPos, 0.70, 1.35, vec2(0.18, 0.03)) * WAVE_SCALE;      // fleurs
    else if (id == 10103 && istopv > 0.5)
        wave = calcMove(worldPos, 0.35, 1.00, vec2(0.20, 0.08)) * WAVE_SCALE;      // cultures
    #endif

    return worldPos + wave;
}

#endif
