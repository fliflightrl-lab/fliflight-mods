package com.fliflight.customcrosshair;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Preset crosshairs and preset colors, applied to the config from the GUI.
 * Each crosshair preset: {shape, color, size, thickness, gap, dot, dotSize}.
 */
public final class CrosshairPresets {
    private CrosshairPresets() {}

    /** Named ready-made crosshairs: name -> {shape, color, size, thickness, gap, dot, dotSize}. */
    public static final Map<String, String[]> CROSSHAIRS = new LinkedHashMap<>();
    /** Named preset colors: name -> ARGB int. */
    public static final Map<String, Integer> COLORS = new LinkedHashMap<>();

    static {
        CROSSHAIRS.put("Classic Cross", new String[]{"cross", "0xFF00FF00", "10", "2", "2", "0", "2"});
        CROSSHAIRS.put("Dot", new String[]{"dot", "0xFF00FF00", "3", "1", "0", "0", "2"});
        CROSSHAIRS.put("X", new String[]{"x", "0xFFFF5555", "10", "2", "2", "0", "2"});
        CROSSHAIRS.put("Circle", new String[]{"circle", "0xFFFFFFFF", "8", "2", "0", "0", "2"});
        CROSSHAIRS.put("T", new String[]{"t", "0xFF55FFFF", "10", "2", "2", "0", "2"});
        CROSSHAIRS.put("Valorant", new String[]{"cross", "0xFF00FF00", "8", "2", "4", "1", "2"});

        COLORS.put("Green", 0xFF00FF00);
        COLORS.put("Red", 0xFFFF5555);
        COLORS.put("Blue", 0xFF5555FF);
        COLORS.put("White", 0xFFFFFFFF);
        COLORS.put("Yellow", 0xFFFFFF55);
        COLORS.put("Cyan", 0xFF55FFFF);
        COLORS.put("Magenta", 0xFFFF55FF);
        COLORS.put("Orange", 0xFFFFAA00);
        COLORS.put("Black", 0xFF000000);
    }
}
