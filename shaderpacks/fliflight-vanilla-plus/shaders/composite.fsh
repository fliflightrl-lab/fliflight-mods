#version 120
/* DRAWBUFFERS:1 */

#include "/lib/config.glsl"

varying vec2 texcoord;

uniform sampler2D colortex0;
uniform float viewWidth;
uniform float viewHeight;

// Seuil de luminance + flou HORIZONTAL. Le flou vertical est fait dans final.fsh,
// ce qui ramene tout le bloom a DEUX passes plein ecran au total.
// Une FONCTION plutot que des variables locales : en GLSL 1.20 on ne peut pas
// redeclarer le meme nom dans la meme portee.
vec3 bright(vec2 uv) {
    vec3 c = texture2D(colortex0, uv).rgb;
    float lum = dot(c, vec3(0.2126, 0.7152, 0.0722));
    return c * (max(lum - BLOOM_THRESHOLD, 0.0) / max(lum, 0.0001));
}

void main() {
    vec2 texel = vec2(1.0 / viewWidth, 1.0 / viewHeight);
    vec2 dir = vec2(1.0, 0.0) * BLOOM_SPREAD * texel;
    vec3 sum = vec3(0.0);
    sum += bright(texcoord - dir * 2.0) * 0.0625;
    sum += bright(texcoord - dir * 1.0) * 0.25;
    sum += bright(texcoord) * 0.375;
    sum += bright(texcoord + dir * 1.0) * 0.25;
    sum += bright(texcoord + dir * 2.0) * 0.0625;
    gl_FragData[0] = vec4(sum * BLOOM_STRENGTH, 1.0);
}
