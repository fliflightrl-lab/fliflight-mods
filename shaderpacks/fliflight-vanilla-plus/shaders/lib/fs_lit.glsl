varying vec2 texCoord;
varying vec2 lmCoord;
varying vec4 vColor;
varying vec3 vNormal;

uniform sampler2D texture;
uniform sampler2D lightmap;

void main() {
    vec4 color = texture2D(texture, texCoord) * vColor;
    color.rgb *= texture2D(lightmap, lmCoord).rgb;
    gl_FragData[0] = color;
}
