package com.fliflight.pvphud;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.network.PlayerListEntry;
import net.minecraft.client.render.RenderTickCounter;

import java.util.Locale;

public class PvPHudClient implements ClientModInitializer {
    public static PvPHudConfig CONFIG;

    @Override
    public void onInitializeClient() {
        CONFIG = PvPHudConfig.load();
        HudRenderCallback.EVENT.register(PvPHudClient::onRenderHud);
    }

    private static void onRenderHud(DrawContext context, RenderTickCounter tickCounter) {
        if (!CONFIG.hudEnabled) return;
        MinecraftClient client = MinecraftClient.getInstance();
        if (client == null || client.player == null || client.options.hudHidden) return;

        int x = 4;
        int y = 4;
        int lineHeight = 10;
        int color = 0xFFFFFF;

        if (CONFIG.hudShowFps) {
            int fps = client.getCurrentFps();
            draw(context, "FPS: " + fps, x, y, color);
            y += lineHeight;
        }
        if (CONFIG.hudShowPing) {
            PlayerListEntry entry = client.getNetworkHandler() != null
                    ? client.getNetworkHandler().getPlayerListEntry(client.player.getUuid())
                    : null;
            int ping = entry != null ? entry.getLatency() : -1;
            draw(context, "Ping: " + ping + "ms", x, y, color);
            y += lineHeight;
        }
        if (CONFIG.hudShowCoords) {
            String coords = String.format(Locale.ROOT, "XYZ: %.0f / %.0f / %.0f",
                    client.player.getX(), client.player.getY(), client.player.getZ());
            draw(context, coords, x, y, color);
            y += lineHeight;
        }
        if (CONFIG.hudShowCps) {
            draw(context, "CPS: " + CpsTracker.getLeftCps() + " / " + CpsTracker.getRightCps(), x, y, color);
        }
    }

    private static void draw(DrawContext context, String text, int x, int y, int color) {
        context.drawText(MinecraftClient.getInstance().textRenderer, text, x, y, color, CONFIG.hudShadow);
    }
}
