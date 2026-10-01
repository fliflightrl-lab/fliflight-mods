#ifndef CONFIG_GLSL
#define CONFIG_GLSL

// ============================================================================
//  Fliflight Vanilla Plus - reglages
//  Tout est expose dans Video Settings -> Shader Options.
//  Les valeurs numeriques sont des sliders, les lignes commentees sont des
//  interrupteurs (decommenter = activer).
// ============================================================================

// ---------- EFFETS ----------
#define BLOOM               // Soft glow around bright areas.
#define WAVES               // Waving grass, leaves, flowers and crops.
#define CUSTOM_SKY          // Sun and moon halo, dawn and dusk horizon band.
#define WATER_WAVES         // Animated swell on the water surface.
#define STARS               // Procedural stars at night.
#define LIGHT_TINT          // Warm torch light, cool sky light.
#define DIRECTIONAL_LIGHT   // Sun-facing surfaces take the colour of the hour.
#define TIME_GRADE          // Warmer dawn and dusk, cooler nights.
#define HORIZON_HAZE        // Blend very distant terrain into the sky colour.
#define FACE_LIGHT          // Light varies with face orientation. Adds depth, costs nothing.
#define TONE_ROLLOFF        // Soft highlight rolloff instead of clipping to white.
#define WATER_SPECULAR      // Sun glints rippling on the water surface.
#define CLOUD_SHADING       // Clouds follow the time of day.
#define UNDERWATER_TINT     // Slight colour shift when the camera is underwater.
//#define SHARPEN           // Unsharp mask. Costs 4 extra texture reads per pixel.
//#define SHADOWS           // NOT SHIPPED: the shadow program is not in this pack. Leave off.

// ---------- BLOOM ----------
#define BLOOM_STRENGTH 0.45       // Bloom intensity [0.0 0.2 0.45 0.7 1.0]
#define BLOOM_THRESHOLD 0.68      // Only brighter than this glows [0.5 0.6 0.68 0.8]
#define BLOOM_SPREAD 2.5          // Bloom width [1.0 1.5 2.5 4.0 6.0]

// ---------- LUMIERE ----------
#define LIGHT_TINT_STRENGTH 0.65  // Warm and cool light strength [0.0 0.35 0.65 1.0]
#define BLOCK_TINT_R 1.18         // Torch light red [0.8 1.0 1.18 1.4]
#define BLOCK_TINT_G 0.98         // Torch light green [0.7 0.9 0.98 1.1]
#define BLOCK_TINT_B 0.76         // Torch light blue [0.5 0.7 0.76 1.0]
#define SKY_TINT_R 0.91           // Sky light red [0.7 0.8 0.91 1.1]
#define SKY_TINT_G 1.00           // Sky light green [0.8 0.9 1.0 1.1]
#define SKY_TINT_B 1.24           // Sky light blue [0.9 1.1 1.24 1.5]
#define DIRECTIONAL_STRENGTH 0.35 // Sun-facing tint strength [0.0 0.2 0.35 0.6]
#define FACE_LIGHT_STRENGTH 1.00  // Face orientation lighting [0.0 0.5 1.0 1.5]
#define FACE_TOP_CONTRAST 0.35    // Top versus bottom faces [0.0 0.2 0.35 0.6]
#define FACE_SUN_CONTRAST 0.30    // Sun-facing versus opposite [0.0 0.2 0.3 0.5]

// ---------- TONE MAPPING ----------
#define TONE_KNEE 0.80            // Where highlights start to roll off [0.6 0.7 0.8 0.9]

// ---------- EAU ----------
#define WATER_WAVE_HEIGHT 0.10    // Swell amplitude in blocks [0.0 0.05 0.10 0.25]
#define WATER_WAVE_SPEED 1.15     // Swell speed [0.5 0.8 1.15 2.0]
#define WATER_SPEC_STRENGTH 0.55  // Sun glint strength [0.0 0.3 0.55 1.0]
#define WATER_SHININESS 96.0      // Glint tightness [32.0 64.0 96.0 160.0]
#define UNDERWATER_STRENGTH 0.18  // Underwater tint [0.0 0.1 0.18 0.35]

// ---------- CIEL ----------
#define SUN_HALO_STRENGTH 0.55    // Sun halo [0.0 0.3 0.55 1.0]
#define MOON_HALO_STRENGTH 0.35   // Moon halo [0.0 0.2 0.35 0.7]
#define STARS_STRENGTH 0.85       // Star brightness [0.0 0.4 0.85 1.5]
#define DUSK_STRENGTH 0.45        // Dawn and dusk horizon band [0.0 0.25 0.45 0.8]

// ---------- BRUME D'HORIZON ----------
#define HAZE_START_BLOCKS 120.0   // Where the haze starts, in blocks [64.0 96.0 120.0 180.0]
#define HAZE_END_BLOCKS 300.0     // Full haze distance, in blocks [200.0 260.0 300.0 400.0]
#define HAZE_STRENGTH 0.85        // Haze strength [0.0 0.5 0.85 1.0]

// ---------- FEUILLAGE ----------
#define WAVE_SCALE 1.00           // Waving amplitude [0.0 0.5 1.0 2.0]

// ---------- ETALONNAGE ----------
#define SATURATION 1.12           // Colour saturation [0.9 1.0 1.12 1.3]
#define CONTRAST 1.05             // Contrast [0.95 1.0 1.05 1.15]
#define BRIGHTNESS 1.02           // Brightness [0.95 1.0 1.02 1.08]
#define SHARPNESS 0.30            // Sharpening amount [0.0 0.15 0.30 0.5]

// ---------- OMBRES ----------
// Le programme d'ombre n'est PAS embarque dans ce pack : garder SHADOWS desactive.
// Ces valeurs ne servent que si le pack est reconstruit avec --shadows.
#define SHADOW_DISTANCE 64.0
#define SHADOW_MAP_RES 1024.0
#define SHADOW_STRENGTH 0.85
#define SHADOW_BIAS_SLOPE 0.25
#define SHADOW_BIAS_DIST 0.004
#define SHADOW_BIAS_MIN 1.0
#define SHADOW_NORMAL_OFF 0.15
#define SHADOW_NORMAL_MAX 0.60

#endif
