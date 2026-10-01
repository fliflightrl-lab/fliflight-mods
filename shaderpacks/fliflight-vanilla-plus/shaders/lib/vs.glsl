#include "/lib/config.glsl"
#include "/lib/waves.glsl"

varying vec2 texCoord;
varying vec2 lmCoord;
varying vec4 vColor;
varying vec3 vNormal;
varying vec3 vWorldPos;
varying float viewDist;

uniform mat4 gbufferModelView;
uniform mat4 gbufferModelViewInverse;

void main() {
    texCoord = (gl_TextureMatrix[0] * gl_MultiTexCoord0).xy;
    lmCoord  = (gl_TextureMatrix[1] * gl_MultiTexCoord1).xy;
    vColor   = gl_Color;

    // gl_NormalMatrix donne la normale en espace VUE. Sans cette conversion,
    // tout calcul monde (decalage d'ombre, produit scalaire avec le soleil)
    // part dans une direction qui depend de l'orientation de la camera.
    vNormal = normalize(mat3(gbufferModelViewInverse) * (gl_NormalMatrix * gl_Normal));

    vec4 viewPos = gl_ModelViewMatrix * gl_Vertex;
    vec3 wPos = (gbufferModelViewInverse * viewPos).xyz;

    #ifdef WAVES
    float istopv = gl_MultiTexCoord0.t < mc_midTexCoord.t ? 1.0 : 0.0;
    wPos = WavingBlocks(wPos, istopv);
    viewPos = gbufferModelView * vec4(wPos, 1.0);
    #endif

    gl_Position = gl_ProjectionMatrix * viewPos;
    vWorldPos = wPos;
    viewDist = length(viewPos.xyz);
}
