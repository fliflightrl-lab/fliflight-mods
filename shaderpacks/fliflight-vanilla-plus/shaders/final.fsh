#version 120

#include "/lib/config.glsl"

varying vec2 texcoord;

uniform sampler2D colortex0;
uniform sampler2D colortex1;
uniform float viewWidth;
uniform float viewHeight;
uniform float sunAngle;

#define SATURATION 1.12
#define CONTRAST   1.05
#define BRIGHTNESS 1.02
#define SHARPNESS  0.30

void main() {
    vec2 texel = vec2(1.0 / viewWidth, 1.0 / viewHeight);
    vec3 color = texture2D(colortex0, texcoord).rgb;

    #ifdef SHARPEN
    vec3 blur = (
        texture2D(colortex0, texcoord + vec2( texel.x, 0.0)).rgb +
        texture2D(colortex0, texcoord - vec2( texel.x, 0.0)).rgb +
        texture2D(colortex0, texcoord + vec2(0.0,  texel.y)).rgb +
        texture2D(colortex0, texcoord - vec2(0.0,  texel.y)).rgb
    ) * 0.25;
    color += (color - blur) * SHARPNESS;
    #endif

    #ifdef BLOOM
    // Flou vertical fusionne ici : composite fait le seuil + le flou horizontal.
    vec2 bdir = vec2(0.0, 1.0) * BLOOM_SPREAD * texel;
    vec3 bloom = vec3(0.0);
    bloom += texture2D(colortex1, texcoord - bdir * 2.0).rgb * 0.0625;
    bloom += texture2D(colortex1, texcoord - bdir * 1.0).rgb * 0.25;
    bloom += texture2D(colortex1, texcoord).rgb * 0.375;
    bloom += texture2D(colortex1, texcoord + bdir * 1.0).rgb * 0.25;
    bloom += texture2D(colortex1, texcoord + bdir * 2.0).rgb * 0.0625;
    color += bloom;
    #endif

    float luma = dot(color, vec3(0.2126, 0.7152, 0.0722));
    color = mix(vec3(luma), color, SATURATION);
    color = (color - 0.5) * CONTRAST + 0.5;
    color *= BRIGHTNESS;

    #ifdef TIME_GRADE
    // Etalonnage selon l'heure : nuits plus froides et legerement desaturees,
    // aube et crepuscule plus chauds.
    float elev = sin(sunAngle * 6.28318530717959);
    float nightAmt = clamp(-elev * 2.5, 0.0, 1.0);
    float duskAmt  = clamp(1.0 - abs(elev) * 4.0, 0.0, 1.0);
    color *= mix(vec3(1.0), vec3(0.86, 0.92, 1.10), nightAmt * 0.55);
    color *= mix(vec3(1.0), vec3(1.08, 0.97, 0.88), duskAmt * 0.45);
    #endif

    gl_FragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}
