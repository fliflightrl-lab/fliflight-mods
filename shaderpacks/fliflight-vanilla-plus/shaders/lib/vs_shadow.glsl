#include "/lib/config.glsl"
#include "/lib/waves.glsl"

varying vec2 texCoord;
varying vec4 vColor;

uniform mat4 gbufferModelViewInverse;
uniform mat4 shadowModelView;
uniform mat4 shadowProjection;

void main() {
    texCoord = gl_MultiTexCoord0.xy;
    vColor = gl_Color;

    vec4 viewPos = gl_ModelViewMatrix * gl_Vertex;
    vec3 wPos = (gbufferModelViewInverse * viewPos).xyz;

    #ifdef WAVES
    float istopv = gl_MultiTexCoord0.t < mc_midTexCoord.t ? 1.0 : 0.0;
    wPos = WavingBlocks(wPos, istopv);
    #endif

    gl_Position = shadowProjection * shadowModelView * vec4(wPos, 1.0);
}
