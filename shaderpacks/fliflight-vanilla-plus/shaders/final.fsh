#version 120

#include "/lib/config.glsl"

varying vec2 texcoord;

uniform sampler2D colortex0;
uniform sampler2D colortex1;
uniform float viewWidth;
uniform float viewHeight;

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
    // Flou vertical fusionne ici : composite fait le seuil + le flou horizontal,
    // final termine le flou vertical et l'ajoute. Une passe plein ecran en moins
    // et 3 lectures en moins par pixel.
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

    gl_FragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}
