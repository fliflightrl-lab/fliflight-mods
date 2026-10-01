#include "/lib/config.glsl"
#include "/lib/space.glsl"
#include "/lib/haze.glsl"

varying vec2 texCoord;
varying vec2 lmCoord;
varying vec4 vColor;
varying vec3 vNormal;
varying vec3 vWorldPos;
varying float viewDist;

uniform sampler2D texture;
uniform sampler2D lightmap;
uniform sampler2D shadowtex1;

#ifdef SHADOWS
float getShadow(vec3 worldPos, vec3 normal, float viewDist) {
    if (viewDist > SHADOW_DISTANCE) return 1.0;        // hors de portee -> eclaire

    vec3 sp = ToShadow(worldPos + normal * 0.06) * 0.5 + 0.5;
    if (sp.x < 0.0 || sp.x > 1.0 || sp.y < 0.0 || sp.y > 1.0 || sp.z < 0.0 || sp.z > 1.0)
        return 1.0;                                    // hors de la shadowmap -> eclaire

    float depth = texture2D(shadowtex1, sp.xy).r;
    if (depth > 0.9999) return 1.0;                    // rien de dessine ici -> eclaire

    float sh = step(sp.z - SHADOW_BIAS, depth);
    // fondu de sortie : evite la bande sombre dure au bord de la shadowmap
    return mix(sh, 1.0, smoothstep(SHADOW_FADE_START, SHADOW_DISTANCE, viewDist));
}
#endif

void main() {
    vec4 color = texture2D(texture, texCoord) * vColor;
    vec3 light = texture2D(lightmap, lmCoord).rgb;

    #ifdef SHADOWS
    float skyFactor = clamp(lmCoord.y * 1.6, 0.0, 1.0);
    float sh = getShadow(vWorldPos, vNormal, viewDist);
    light *= mix(1.0, sh, SHADOW_STRENGTH * skyFactor);
    #endif

    color.rgb *= light;
    color.rgb = applyHaze(color.rgb, viewDist);
    gl_FragData[0] = color;
}
