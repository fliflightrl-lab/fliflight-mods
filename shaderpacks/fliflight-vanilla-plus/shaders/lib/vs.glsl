varying vec2 texCoord;
varying vec2 lmCoord;
varying vec4 vColor;
varying vec3 vNormal;

void main() {
    texCoord = (gl_TextureMatrix[0] * gl_MultiTexCoord0).xy;
    lmCoord  = (gl_TextureMatrix[1] * gl_MultiTexCoord1).xy;
    vColor   = gl_Color;
    vNormal  = normalize(gl_NormalMatrix * gl_Normal);
    gl_Position = ftransform();
}
