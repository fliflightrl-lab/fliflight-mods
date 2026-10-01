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

void main() {
    vec4 color = texture2D(texture, texCoord) * vColor;

    #ifdef CLOUD_SHADING
    float elev = sunElevation();
    float dayAmt  = clamp(elev * 2.5, 0.0, 1.0);
    float duskAmt = clamp(1.0 - abs(elev) * 4.0, 0.0, 1.0);
    // Modulation autour de 1.0 : on ne double-assombrit pas ce que le ciel fait deja.
    vec3 tint = mix(vec3(0.80, 0.85, 1.00), vec3(1.10, 1.00, 0.90), dayAmt);
    tint *= mix(vec3(1.0), vec3(1.15, 0.92, 0.74), duskAmt * 0.6);
    color.rgb *= tint;
    #endif

    color.rgb = applyHaze(color.rgb, viewDist);
    gl_FragData[0] = color;
}
