package com.fliflight.pvpqol;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import net.fabricmc.loader.api.FabricLoader;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class PvPQolConfig {
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();

    public boolean hudEnabled = true;
    public boolean hudShowFps = true;
    public boolean hudShowPing = true;
    public boolean hudShowCoords = true;
    public boolean hudShadow = true;

    public boolean lowerFireEnabled = true;
    /** Extra downward offset applied to the fire overlay. 0.0 = vanilla. Larger = lower flame. */
    public float fireLowerOffset = 0.35f;

    public boolean noPumpkinBlur = true;

    public transient Path configPath;

    public static PvPQolConfig load() {
        Path path = FabricLoader.getInstance().getConfigDir().resolve("pvpqol.json");
        PvPQolConfig config;
        if (Files.exists(path)) {
            try {
                config = GSON.fromJson(Files.readString(path), PvPQolConfig.class);
            } catch (Exception e) {
                config = new PvPQolConfig();
            }
        } else {
            config = new PvPQolConfig();
        }
        if (config == null) config = new PvPQolConfig();
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
}
