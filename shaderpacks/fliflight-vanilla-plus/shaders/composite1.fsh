#version 120
/* DRAWBUFFERS:2 */

#include "/lib/config.glsl"

varying vec2 texcoord;

uniform sampler2D colortex1;
uniform float viewWidth;
uniform float viewHeight;

void main() {
    vec2 texel = vec2(1.0 / viewWidth, 1.0 / viewHeight);
    vec3 sum = vec3(0.0);
    sum += texture2D(colortex1, texcoord + vec2(1.0, 0.0) * -2.0 * BLOOM_SPREAD * texel).rgb * 0.0625;
    sum += texture2D(colortex1, texcoord + vec2(1.0, 0.0) * -1.0 * BLOOM_SPREAD * texel).rgb * 0.25;
    sum += texture2D(colortex1, texcoord + vec2(1.0, 0.0) * 0.0 * BLOOM_SPREAD * texel).rgb * 0.375;
    sum += texture2D(colortex1, texcoord + vec2(1.0, 0.0) * 1.0 * BLOOM_SPREAD * texel).rgb * 0.25;
    sum += texture2D(colortex1, texcoord + vec2(1.0, 0.0) * 2.0 * BLOOM_SPREAD * texel).rgb * 0.0625;
    gl_FragData[0] = vec4(sum, 1.0);
}
