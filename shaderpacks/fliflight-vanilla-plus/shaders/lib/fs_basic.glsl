#include "/lib/config.glsl"
#include "/lib/haze.glsl"

varying vec2 texCoord;
varying vec2 lmCoord;
varying vec4 vColor;
varying vec3 vWorldPos;
varying float viewDist;

uniform sampler2D lightmap;

void main() {
    vec4 color = vec4(vColor.rgb * texture2D(lightmap, lmCoord).rgb, vColor.a);
    color.rgb = applyHaze(color.rgb, viewDist);
    gl_FragData[0] = color;
}
