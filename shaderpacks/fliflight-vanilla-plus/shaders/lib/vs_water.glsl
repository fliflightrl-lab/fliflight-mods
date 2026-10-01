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
    vNormal = normalize(mat3(gbufferModelViewInverse) * (gl_NormalMatrix * gl_Normal));

    vec4 viewPos = gl_ModelViewMatrix * gl_Vertex;
    vec3 wPos = (gbufferModelViewInverse * viewPos).xyz;

    #ifdef WAVES
    float istopv = gl_MultiTexCoord0.t < mc_midTexCoord.t ? 1.0 : 0.0;
    wPos = WavingBlocks(wPos, istopv);
    #endif

    #ifdef WATER_WAVES
    // Face du dessus uniquement. La houle est fonction de la POSITION MONDE :
    // continue d'un chunk a l'autre, aucune couture visible.
    if (vNormal.y > 0.5) {
        float w = sin(wPos.x * 0.65 + frameTimeCounter * WATER_WAVE_SPEED)
                + cos(wPos.z * 0.55 + frameTimeCounter * WATER_WAVE_SPEED * 0.74);
        wPos.y += w * WATER_WAVE_HEIGHT;
    }
    #endif

    viewPos = gbufferModelView * vec4(wPos, 1.0);
    gl_Position = gl_ProjectionMatrix * viewPos;
    vWorldPos = wPos;
    viewDist = length(viewPos.xyz);
    viewDir = normalize(wPos - gbufferModelViewInverse[3].xyz);
    isWater = 1.0;
}
