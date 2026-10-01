#include "/lib/config.glsl"
#include "/lib/space.glsl"

varying vec2 texCoord;
varying vec2 lmCoord;
varying vec4 vColor;
varying vec3 vNormal;
varying vec3 vWorldPos;

uniform sampler2D texture;
uniform sampler2D lightmap;
uniform sampler2D shadowtex1;

void main() {
    vec4 color = texture2D(texture, texCoord) * vColor;
    vec3 light = texture2D(lightmap, lmCoord).rgb;

    #ifdef SHADOWS
    vec3 shadowPos = ToShadow(vWorldPos + vNormal * 0.06) * 0.5 + 0.5;
    float sh = 1.0;
    if (all(greaterThan(shadowPos, vec3(0.0))) && all(lessThan(shadowPos, vec3(1.0)))) {
        float depth = texture2D(shadowtex1, shadowPos.xy).r;
        sh = step(shadowPos.z - 0.0006, depth);
    }
    float skyFactor = clamp(lmCoord.y * 1.6, 0.0, 1.0);
    light *= mix(1.0, sh, SHADOW_STRENGTH * skyFactor);
    #endif

    color.rgb *= light;
    gl_FragData[0] = color;
}
