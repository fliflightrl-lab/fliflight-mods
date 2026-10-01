#ifndef SPACE_GLSL
#define SPACE_GLSL

#define diagonal3(m) vec3((m)[0].x, (m)[1].y, (m)[2].z)
#define projMAD(m, v) (diagonal3(m) * (v) + (m)[3].xyz)

uniform mat4 gbufferProjectionInverse;
uniform mat4 gbufferModelViewInverse;
uniform mat4 shadowProjection;
uniform mat4 shadowModelView;

uniform float sunAngle;
uniform float sunPathRotation;

vec3 ToNDC(vec3 pos) {
    vec4 iProjDiag = vec4(gbufferProjectionInverse[0].x, gbufferProjectionInverse[1].y, gbufferProjectionInverse[2].zw);
    vec3 p3 = pos * 2.0 - 1.0;
    vec4 viewPos = iProjDiag * p3.xyzz + gbufferProjectionInverse[3];
    return viewPos.xyz / viewPos.w;
}

vec3 ToWorld(vec3 pos) {
    return mat3(gbufferModelViewInverse) * pos + gbufferModelViewInverse[3].xyz;
}

vec3 ToShadow(vec3 pos) {
    vec3 shadowpos = mat3(shadowModelView) * pos + shadowModelView[3].xyz;
    return projMAD(shadowProjection, shadowpos);
}

vec3 getSunDir() {
    float ang = sunAngle * 6.28318530717959;
    float sr = sunPathRotation * 0.01745329251994;
    return vec3(cos(ang), sin(ang) * cos(sr), sin(ang) * sin(sr));
}

#endif
