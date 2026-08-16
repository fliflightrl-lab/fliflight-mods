package com.fliflight.pvphud;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import net.fabricmc.loader.api.FabricLoader;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class PvPHudConfig {
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();

    public boolean hudEnabled = true;
    public boolean hudShowFps = true;
    public boolean hudShowPing = true;
    public boolean hudShowCoords = true;
    public boolean hudShowCps = true;
    public boolean hudShadow = true;

    public transient Path configPath;

    public static PvPHudConfig load() {
        Path path = FabricLoader.getInstance().getConfigDir().resolve("pvphud.json");
        PvPHudConfig config;
        if (Files.exists(path)) {
            try {
                config = GSON.fromJson(Files.readString(path), PvPHudConfig.class);
            } catch (Exception e) {
                config = new PvPHudConfig();
            }
        } else {
            config = new PvPHudConfig();
        }
        if (config == null) config = new PvPHudConfig();
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
