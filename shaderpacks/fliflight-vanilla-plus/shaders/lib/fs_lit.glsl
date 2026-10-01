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
float getShadow(vec3 worldPos, vec3 normal, float viewDist, float skyFactor) {
    if (viewDist > SHADOW_DISTANCE) return 1.0;
    if (skyFactor < 0.001) return 1.0;

    vec3 sunDir = getSunDir();
    float NoL = dot(normal, sunDir);
    if (NoL <= 0.0) return 0.0;

    float biasFactor = sqrt(1.0 - NoL * NoL) / max(NoL, 0.05);
    float nOffset = min(SHADOW_NORMAL_OFF * (1.0 + biasFactor * 0.4), SHADOW_NORMAL_MAX);
    vec3 sp = ToShadow(worldPos + normal * nOffset) * 0.5 + 0.5;

    if (sp.x <= 0.0 || sp.x >= 1.0 || sp.y <= 0.0 || sp.y >= 1.0 || sp.z <= 0.0 || sp.z >= 1.0)
        return 1.0;

    float depth = texture2D(shadowtex1, sp.xy).r;
    if (depth > 0.9999) return 1.0;

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

    float blockAmt = lmCoord.x;
    float skyAmt   = lmCoord.y;

    #ifdef LIGHT_TINT
    // Aucune lecture de texture en plus : on teinte l'echantillon unique d'apres
    // le poids relatif de la lumiere de bloc et de la lumiere du ciel.
    vec3 tint = (BLOCK_TINT * blockAmt + SKY_TINT * skyAmt) / max(blockAmt + skyAmt, 0.0001);
    light *= mix(vec3(1.0), tint, LIGHT_TINT_STRENGTH);
    #endif

    #ifdef DIRECTIONAL_LIGHT
    // Le cote expose au soleil prend la couleur de l'heure (dore au coucher,
    // bleute la nuit). Remplace une bonne part de l'interet des ombres, sans passe d'ombre.
    float sunFace = clamp(dot(vNormal, getSunDir()) * 0.5 + 0.5, 0.0, 1.0);
    light *= mix(vec3(1.0), getSunColor(), DIRECTIONAL_STRENGTH * skyAmt * sunFace);
    #endif

    #ifdef SHADOWS
    float skyFactor = clamp(skyAmt * 1.6, 0.0, 1.0);
    float sh = getShadow(vWorldPos, vNormal, viewDist, skyFactor);
    light *= mix(1.0, sh, SHADOW_STRENGTH * skyFactor);
    #endif

    color.rgb *= light;
    color.rgb = applyHaze(color.rgb, viewDist);
    gl_FragData[0] = color;
}
