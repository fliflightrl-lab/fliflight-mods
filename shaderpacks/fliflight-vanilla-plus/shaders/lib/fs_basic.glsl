varying vec2 texCoord;
varying vec2 lmCoord;
varying vec4 vColor;

uniform sampler2D lightmap;

void main() {
    vec4 color = vColor;
    color.rgb *= texture2D(lightmap, lmCoord).rgb;
    gl_FragData[0] = color;
}
