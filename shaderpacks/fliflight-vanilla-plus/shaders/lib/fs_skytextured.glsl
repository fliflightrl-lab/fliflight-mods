#include "/lib/config.glsl"

varying vec2 texCoord;
varying vec2 lmCoord;
varying vec4 vColor;

uniform sampler2D texture;

void main() {
    vec4 color = texture2D(texture, texCoord) * vColor;
    #ifdef CUSTOM_SKY
    color.rgb *= 1.18;
    #endif
    gl_FragData[0] = color;
}
