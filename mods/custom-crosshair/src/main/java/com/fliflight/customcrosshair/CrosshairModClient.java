package com.fliflight.customcrosshair;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.option.KeyBinding;
import net.minecraft.client.render.RenderTickCounter;
import net.minecraft.client.util.InputUtil;
import org.lwjgl.glfw.GLFW;

public class CrosshairModClient implements ClientModInitializer {
    public static CrosshairConfig CONFIG;

    private static KeyBinding openScreenKey;

    @Override
    public void onInitializeClient() {
        CONFIG = CrosshairConfig.load();

        openScreenKey = KeyBindingHelper.registerKeyBinding(new KeyBinding(
                "key.custom-crosshair.open",
                InputUtil.Type.KEYSYM,
                GLFW.GLFW_KEY_C,
                "category.custom-crosshair"
        ));

        HudRenderCallback.EVENT.register(CrosshairModClient::onRender);

        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            while (openScreenKey.wasPressed()) {
                client.setScreen(new CrosshairScreen(CONFIG, client.currentScreen));
            }
        });
    }

    private static void onRender(DrawContext context, RenderTickCounter tickCounter) {
        if (!CONFIG.enabled) return;
        MinecraftClient client = MinecraftClient.getInstance();
        if (client == null || client.player == null) return;
        if (!client.options.getPerspective().isFirstPerson()) return;

        int cx = context.getScaledWindowWidth() / 2;
        int cy = context.getScaledWindowHeight() / 2;
        CrosshairRenderer.render(context, cx, cy, CONFIG);
    }
}
