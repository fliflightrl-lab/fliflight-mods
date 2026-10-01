#include "/lib/config.glsl"
#include "/lib/space.glsl"
#include "/lib/haze.glsl"

varying vec2 texCoord;
varying vec2 lmCoord;
varying vec4 vColor;
varying vec3 vNormal;
varying vec3 vWorldPos;
varying float viewDist;
varying vec3 viewDir;
varying float isWater;

uniform sampler2D texture;
uniform sampler2D lightmap;
uniform sampler2D shadowtex1;
uniform float frameTimeCounter;
uniform int isEyeInWater;

const vec3 BLOCK_TINT = vec3(BLOCK_TINT_R, BLOCK_TINT_G, BLOCK_TINT_B);
const vec3 SKY_TINT   = vec3(SKY_TINT_R, SKY_TINT_G, SKY_TINT_B);

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
    return mix(sh, 1.0, smoothstep(SHADOW_DISTANCE * 0.70, SHADOW_DISTANCE, viewDist));
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

    vec3 sunDir = getSunDir();
    float sunFace = clamp(dot(vNormal, sunDir) * 0.5 + 0.5, 0.0, 1.0);

    #ifdef DIRECTIONAL_LIGHT
    light *= mix(vec3(1.0), getSunColor(), DIRECTIONAL_STRENGTH * skyAmt * sunFace);
    #endif

    #ifdef FACE_LIGHT
    // Le lightmap de Minecraft ne varie pas selon l'orientation de la face : toutes
    // les faces d'un bloc recoivent la meme lumiere. On l'ajoute ici.
    // Cout : aucune lecture de texture, aucun branchement.
    float topness = clamp(vNormal.y * 0.5 + 0.5, 0.0, 1.0);
    float faceLight = 1.0
        + (topness - 0.5) * FACE_TOP_CONTRAST
        + (sunFace - 0.5) * FACE_SUN_CONTRAST;
    light *= mix(1.0, faceLight, skyAmt * FACE_LIGHT_STRENGTH);
    #endif

    #ifdef SHADOWS
    float skyFactor = clamp(skyAmt * 1.6, 0.0, 1.0);
    float sh = getShadow(vWorldPos, vNormal, viewDist, skyFactor);
    light *= mix(1.0, sh, SHADOW_STRENGTH * skyFactor);
    #endif

    color.rgb *= light;

    #ifdef WATER_SPECULAR
    // Reflet du soleil sur l'eau, normale ondulee par deux sinus croises.
    // Uniquement sur les fragments d'eau : isWater vient du vertex shader.
    if (isWater > 0.5) {
        float ripple = sin(vWorldPos.x * 2.3 + frameTimeCounter * 1.7)
                     * cos(vWorldPos.z * 2.1 + frameTimeCounter * 1.3);
        vec3 n = normalize(vNormal + vec3(ripple * 0.08, 0.0, ripple * 0.08));
        vec3 halfVec = normalize(sunDir - viewDir);
        float spec = pow(max(dot(n, halfVec), 0.0), WATER_SHININESS);
        color.rgb += getSunColor() * spec * WATER_SPEC_STRENGTH * skyAmt;
    }
    #endif

    #ifdef UNDERWATER_TINT
    if (isEyeInWater == 1) {
        color.rgb = mix(color.rgb, color.rgb * vec3(0.72, 0.90, 1.05), UNDERWATER_STRENGTH);
    }
    #endif

    color.rgb = applyHaze(color.rgb, viewDist);
    gl_FragData[0] = color;
}
