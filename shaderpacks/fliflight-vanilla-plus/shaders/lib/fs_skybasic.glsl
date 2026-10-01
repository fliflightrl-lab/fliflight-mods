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

    float sunAmount = max(dot(worldDir, sunDir), 0.0);
    float horizon = pow(1.0 - clamp(abs(worldDir.y), 0.0, 1.0), 5.0);

    color += vec3(1.00, 0.72, 0.42) * pow(sunAmount, 14.0) * SUN_HALO_STRENGTH;
    color += vec3(1.00, 0.52, 0.22) * horizon * pow(sunAmount, 2.5) * 0.35;
    #endif

    gl_FragData[0] = vec4(color, vColor.a);
}
