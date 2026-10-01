#include "/lib/config.glsl"
#include "/lib/space.glsl"

varying vec2 texCoord;
varying vec2 lmCoord;
varying vec4 vColor;

uniform float viewWidth;
uniform float viewHeight;

void main() {
    vec3 color = vColor.rgb;

    #ifdef CUSTOM_SKY
    vec3 screenPos = vec3(gl_FragCoord.xy / vec2(viewWidth, viewHeight), 1.0);
    vec3 viewRay = ToNDC(screenPos);
    vec3 worldDir = normalize(mat3(gbufferModelViewInverse) * viewRay);
    vec3 sunDir = getSunDir();

    float elev = sunElevation();
    float dayAmt   = clamp(elev * 2.5, 0.0, 1.0);
    float nightAmt = clamp(-elev * 2.5, 0.0, 1.0);

    float sunAmount  = max(dot(worldDir, sunDir), 0.0);
    float moonAmount = max(dot(worldDir, -sunDir), 0.0);
    float horizon = pow(1.0 - clamp(abs(worldDir.y), 0.0, 1.0), 5.0);

    // halo solaire
    color += vec3(1.00, 0.72, 0.42) * pow(sunAmount, 14.0) * SUN_HALO_STRENGTH;

    // bande chaude a l'horizon cote soleil : rouge profond a l'aube/c repuscule,
    // plus douce en pleine journee
    vec3 duskTint = mix(vec3(1.00, 0.42, 0.18), vec3(1.00, 0.78, 0.50), dayAmt);
    color += duskTint * horizon * pow(sunAmount, 3.0) * DUSK_STRENGTH * (1.0 - nightAmt);

    #ifdef STARS
    // Etoiles : bruit par cellule de direction, sans branchement (pas de divergence).
    // Une cellule sur ~80 a un "h" au-dessus du seuil : elle contient une etoile.
    vec3 sd = worldDir * 220.0;
    vec3 cell = floor(sd);
    vec3 fr = fract(sd) - 0.5;
    float h = fract(sin(dot(cell, vec3(12.9898, 78.233, 37.719))) * 43758.5453);
    float star = smoothstep(0.10, 0.0, length(fr)) * step(0.988, h);
    color += vec3(0.85, 0.90, 1.00) * star * STARS_STRENGTH * nightAmt
             * clamp(worldDir.y * 3.0, 0.0, 1.0);
    #endif

    // halo lunaire (la lune est a l'oppose du soleil)
    color += vec3(0.55, 0.65, 0.90) * pow(moonAmount, 24.0) * MOON_HALO_STRENGTH * nightAmt;
    #endif

    gl_FragData[0] = vec4(color, vColor.a);
}
