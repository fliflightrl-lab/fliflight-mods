varying vec2 texCoord;
varying vec2 lmCoord;
varying vec4 vColor;
varying vec3 vNormal;

uniform sampler2D texture;

void main() {
    gl_FragData[0] = texture2D(texture, texCoord) * vColor;
}
