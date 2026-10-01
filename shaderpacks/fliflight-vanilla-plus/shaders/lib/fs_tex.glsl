#include "/lib/config.glsl"
#include "/lib/haze.glsl"

varying vec2 texCoord;
varying vec2 lmCoord;
varying vec4 vColor;
varying vec3 vWorldPos;
varying float viewDist;

uniform sampler2D texture;

void main() {
    vec4 color = texture2D(texture, texCoord) * vColor;
    color.rgb = applyHaze(color.rgb, viewDist);
    gl_FragData[0] = color;
}
