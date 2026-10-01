#include "/lib/config.glsl"

varying vec2 texCoord;
varying vec4 vColor;

// ATTENTION : dans un programme d'ombre OptiFine, le sampler s'appelle `texture`.
// L'appeler `tex` donne un sampler non lie -> test alpha faux.
uniform sampler2D texture;

void main() {
    vec4 color = texture2D(texture, texCoord) * vColor;
    if (color.a < 0.1) discard;
    gl_FragData[0] = color;
}
