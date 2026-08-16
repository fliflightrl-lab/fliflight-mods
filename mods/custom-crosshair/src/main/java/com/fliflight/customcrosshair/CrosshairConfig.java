package com.fliflight.customcrosshair;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import net.fabricmc.loader.api.FabricLoader;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class CrosshairConfig {
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();

    public boolean enabled = true;

    /** Shape: "cross", "dot", "x", "circle", "t". */
    public String shape = "cross";

    /** Color as 0xAARRGGBB int (alpha ignored, drawn opaque). */
    public int color = 0xFF00FF00;

    /** Half-length (radius) of the crosshair in pixels. */
    public int size = 10;

    /** Thickness of the lines in pixels. */
    public int thickness = 2;

    /** Gap at the center (for cross/t/x) in pixels. */
    public int gap = 2;

    public transient Path configPath;

    public static CrosshairConfig load() {
        Path path = FabricLoader.getInstance().getConfigDir().resolve("custom-crosshair.json");
        CrosshairConfig config;
        if (Files.exists(path)) {
            try {
                config = GSON.fromJson(Files.readString(path), CrosshairConfig.class);
            } catch (Exception e) {
                config = new CrosshairConfig();
            }
        } else {
            config = new CrosshairConfig();
        }
        if (config == null) config = new CrosshairConfig();
        config.configPath = path;
        config.save();
        return config;
    }

    public void save() {
        if (configPath == null) return;
        try {
            Files.writeString(configPath, GSON.toJson(this));
        } catch (IOException ignored) {
        }
    }

    public int getRgbColor() {
        return color | 0xFF000000;
    }
}
