#version 120
/* DRAWBUFFERS:2 */

varying vec2 texcoord;

uniform sampler2D colortex1;
uniform float viewWidth;
uniform float viewHeight;

void main() {
    vec2 texel = vec2(1.0 / viewWidth, 1.0 / viewHeight);
    vec3 sum = vec3(0.0);
    sum += texture2D(colortex1, texcoord + vec2(1.0, 0.0) * -4.0 * 4.0 * texel).rgb * 0.0162;
    sum += texture2D(colortex1, texcoord + vec2(1.0, 0.0) * -3.0 * 4.0 * texel).rgb * 0.054;
    sum += texture2D(colortex1, texcoord + vec2(1.0, 0.0) * -2.0 * 4.0 * texel).rgb * 0.1216;
    sum += texture2D(colortex1, texcoord + vec2(1.0, 0.0) * -1.0 * 4.0 * texel).rgb * 0.1946;
    sum += texture2D(colortex1, texcoord + vec2(1.0, 0.0) * 0.0 * 4.0 * texel).rgb * 0.227;
    sum += texture2D(colortex1, texcoord + vec2(1.0, 0.0) * 1.0 * 4.0 * texel).rgb * 0.1946;
    sum += texture2D(colortex1, texcoord + vec2(1.0, 0.0) * 2.0 * 4.0 * texel).rgb * 0.1216;
    sum += texture2D(colortex1, texcoord + vec2(1.0, 0.0) * 3.0 * 4.0 * texel).rgb * 0.054;
    sum += texture2D(colortex1, texcoord + vec2(1.0, 0.0) * 4.0 * 4.0 * texel).rgb * 0.0162;
    gl_FragData[0] = vec4(sum, 1.0);
}
