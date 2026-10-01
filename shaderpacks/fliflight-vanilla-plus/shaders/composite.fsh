#version 120
/* DRAWBUFFERS:1 */

#include "/lib/config.glsl"

varying vec2 texcoord;

uniform sampler2D colortex0;
uniform float viewWidth;
uniform float viewHeight;

// Seuil de luminance applique A CHAQUE ETAPE du flou horizontal : le bright-pass
// et le flou H sont fusionnes, ce qui supprime une passe plein ecran.
void main() {
    vec2 texel = vec2(1.0 / viewWidth, 1.0 / viewHeight);
    vec3 sum = vec3(0.0);
    vec3 s = texture2D(colortex0, texcoord + vec2(1.0, 0.0) * -2.0 * BLOOM_SPREAD * texel).rgb;
    float l = dot(s, vec3(0.2126, 0.7152, 0.0722));
    sum += s * (max(l - BLOOM_THRESHOLD, 0.0) / max(l, 0.0001)) * 0.0625;
    vec3 s = texture2D(colortex0, texcoord + vec2(1.0, 0.0) * -1.0 * BLOOM_SPREAD * texel).rgb;
    float l = dot(s, vec3(0.2126, 0.7152, 0.0722));
    sum += s * (max(l - BLOOM_THRESHOLD, 0.0) / max(l, 0.0001)) * 0.25;
    vec3 s = texture2D(colortex0, texcoord + vec2(1.0, 0.0) * 0.0 * BLOOM_SPREAD * texel).rgb;
    float l = dot(s, vec3(0.2126, 0.7152, 0.0722));
    sum += s * (max(l - BLOOM_THRESHOLD, 0.0) / max(l, 0.0001)) * 0.375;
    vec3 s = texture2D(colortex0, texcoord + vec2(1.0, 0.0) * 1.0 * BLOOM_SPREAD * texel).rgb;
    float l = dot(s, vec3(0.2126, 0.7152, 0.0722));
    sum += s * (max(l - BLOOM_THRESHOLD, 0.0) / max(l, 0.0001)) * 0.25;
    vec3 s = texture2D(colortex0, texcoord + vec2(1.0, 0.0) * 2.0 * BLOOM_SPREAD * texel).rgb;
    float l = dot(s, vec3(0.2126, 0.7152, 0.0722));
    sum += s * (max(l - BLOOM_THRESHOLD, 0.0) / max(l, 0.0001)) * 0.0625;
    gl_FragData[0] = vec4(sum * BLOOM_STRENGTH, 1.0);
}
