varying vec2 texCoord;
varying vec4 vColor;

uniform sampler2D tex;

void main() {
    vec4 color = texture2D(tex, texCoord) * vColor;
    if (color.a < 0.1) discard;
    gl_FragData[0] = color;
}
