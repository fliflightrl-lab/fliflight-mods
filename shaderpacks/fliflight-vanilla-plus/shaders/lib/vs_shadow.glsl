#include "/lib/config.glsl"
#include "/lib/waves.glsl"

varying vec2 texCoord;
varying vec4 vColor;

uniform mat4 shadowModelView;
uniform mat4 shadowModelViewInverse;
uniform mat4 shadowProjection;

void main() {
    texCoord = gl_MultiTexCoord0.xy;
    vColor = gl_Color;

    // CORRECTIF MAJEUR. Dans une passe d'ombre, gl_ModelViewMatrix EST la matrice
    // d'ombre (shadowModelView), PAS celle du gbuffer. Utiliser gbufferModelViewInverse
    // dessus donnait une position monde absurde : la shadowmap etait remplie de
    // geometrie placee n'importe ou -> "une grosse ombre etrange" face au soleil.
    // BSL doit inverser DEUX matrices (shadowModelViewInverse * shadowProjectionInverse
    // * ftransform()) ; ici il suffit d'inverser la modelview, gl_Vertex etant deja
    // passe par elle.
    vec4 worldPos = shadowModelViewInverse * (gl_ModelViewMatrix * gl_Vertex);
    vec3 wPos = worldPos.xyz;

    #ifdef WAVES
    float istopv = gl_MultiTexCoord0.t < mc_midTexCoord.t ? 1.0 : 0.0;
    wPos = WavingBlocks(wPos, istopv);
    #endif

    gl_Position = shadowProjection * shadowModelView * vec4(wPos, 1.0);
}
