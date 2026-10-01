#version 120
/* DRAWBUFFERS:1 */

#include "/lib/config.glsl"

varying vec2 texcoord;

uniform sampler2D colortex0;

void main() {
    vec3 color = texture2D(colortex0, texcoord).rgb;
    float lum = dot(color, vec3(0.2126, 0.7152, 0.0722));
    float factor = max(lum - BLOOM_THRESHOLD, 0.0) / max(lum, 0.0001);
    gl_FragData[0] = vec4(color * factor * BLOOM_STRENGTH, 1.0);
}
