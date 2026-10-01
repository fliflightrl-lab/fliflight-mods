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
// normal : espace MONDE. viewDist : distance camera (espace vue).
// skyFactor : 0 = eclairage artificiel, 1 = plein ciel.
float getShadow(vec3 worldPos, vec3 normal, float viewDist, float skyFactor) {
    if (viewDist > SHADOW_DISTANCE) return 1.0;        // hors de portee
    if (skyFactor < 0.001) return 1.0;                 // sous terre / interieur : pas d'ombre solaire

    vec3 sunDir = getSunDir();
    float NoL = dot(normal, sunDir);
    if (NoL <= 0.0) return 0.0;                        // face a l'oppose du soleil -> sombre, sans lecture

    // biais proportionnel a la pente, comme BSL : tan(angle) = sqrt(1-NoL^2)/NoL
    float biasFactor = sqrt(1.0 - NoL * NoL) / max(NoL, 0.05);

    // 1) decalage le long de la normale, en blocs -> previsible, tue l'acne
    float nOffset = min(SHADOW_NORMAL_OFF * (1.0 + biasFactor * 0.4), SHADOW_NORMAL_MAX);
    vec3 sp = ToShadow(worldPos + normal * nOffset) * 0.5 + 0.5;

    if (sp.x <= 0.0 || sp.x >= 1.0 || sp.y <= 0.0 || sp.y >= 1.0 || sp.z <= 0.0 || sp.z >= 1.0)
        return 1.0;                                    // hors de la shadowmap

    float depth = texture2D(shadowtex1, sp.xy).r;
    if (depth > 0.9999) return 1.0;                    // rien de dessine ici

    // 2) biais de profondeur, lui aussi proportionnel a la pente
    float depthBias = (SHADOW_BIAS_SLOPE * biasFactor
                       + SHADOW_BIAS_DIST * viewDist
                       + SHADOW_BIAS_MIN) / SHADOW_MAP_RES;

    float sh = step(sp.z - depthBias, depth);
    return mix(sh, 1.0, smoothstep(SHADOW_FADE_START, SHADOW_DISTANCE, viewDist));
}
#endif

void main() {
    vec4 color = texture2D(texture, texCoord) * vColor;
    vec3 light = texture2D(lightmap, lmCoord).rgb;

    #ifdef SHADOWS
    float skyFactor = clamp(lmCoord.y * 1.6, 0.0, 1.0);
    float sh = getShadow(vWorldPos, vNormal, viewDist, skyFactor);
    light *= mix(1.0, sh, SHADOW_STRENGTH * skyFactor);
    #endif

    color.rgb *= light;
    color.rgb = applyHaze(color.rgb, viewDist);
    gl_FragData[0] = color;
}
