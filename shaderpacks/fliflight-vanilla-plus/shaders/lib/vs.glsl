#include "/lib/config.glsl"
#include "/lib/waves.glsl"

varying vec2 texCoord;
varying vec2 lmCoord;
varying vec4 vColor;
varying vec3 vNormal;
varying vec3 vWorldPos;
varying float viewDist;
varying vec3 viewDir;
varying float isWater;

uniform mat4 gbufferModelView;
uniform mat4 gbufferModelViewInverse;

void main() {
    texCoord = (gl_TextureMatrix[0] * gl_MultiTexCoord0).xy;
    lmCoord  = (gl_TextureMatrix[1] * gl_MultiTexCoord1).xy;
    vColor   = gl_Color;

    // gl_NormalMatrix donne la normale en espace VUE : conversion obligatoire
    // avant tout calcul en espace monde.
    vNormal = normalize(mat3(gbufferModelViewInverse) * (gl_NormalMatrix * gl_Normal));

    vec4 viewPos = gl_ModelViewMatrix * gl_Vertex;
    vec3 wPos = (gbufferModelViewInverse * viewPos).xyz;

    #ifdef WAVES
    float istopv = gl_MultiTexCoord0.t < mc_midTexCoord.t ? 1.0 : 0.0;
    wPos = WavingBlocks(wPos, istopv);
    #endif

    viewPos = gbufferModelView * vec4(wPos, 1.0);
    gl_Position = gl_ProjectionMatrix * viewPos;
    vWorldPos = wPos;
    viewDist = length(viewPos.xyz);
    // La camera en espace monde est la translation de la matrice inverse.
    // Aucune dependance a `cameraPosition`, qui peut valoir 0.
    viewDir = normalize(wPos - gbufferModelViewInverse[3].xyz);
    isWater = 0.0;
}
