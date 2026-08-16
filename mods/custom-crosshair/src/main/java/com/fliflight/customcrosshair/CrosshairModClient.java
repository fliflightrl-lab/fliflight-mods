package com.fliflight.customcrosshair;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.render.RenderTickCounter;
import net.minecraft.client.util.math.MatrixStack;
import net.minecraft.util.math.RotationAxis;

public class CrosshairModClient implements ClientModInitializer {
    public static CrosshairConfig CONFIG;

    @Override
    public void onInitializeClient() {
        CONFIG = CrosshairConfig.load();
        HudRenderCallback.EVENT.register(CrosshairModClient::onRender);
    }

    private static void onRender(DrawContext context, RenderTickCounter tickCounter) {
        if (!CONFIG.enabled) return;
        MinecraftClient client = MinecraftClient.getInstance();
        if (client == null || client.player == null) return;
        // Only render in first person (vanilla crosshair is also first-person only).
        if (!client.options.getPerspective().isFirstPerson()) return;

        int cx = context.getScaledWindowWidth() / 2;
        int cy = context.getScaledWindowHeight() / 2;
        int color = CONFIG.getRgbColor();
        int size = CONFIG.size;
        int t = CONFIG.thickness;
        int gap = CONFIG.gap;

        switch (CONFIG.shape.toLowerCase()) {
            case "dot" -> drawDot(context, cx, cy, size, color);
            case "x" -> drawX(context, cx, cy, size, t, gap, color);
            case "circle" -> drawCircle(context, cx, cy, size, t, color);
            case "t" -> drawT(context, cx, cy, size, t, gap, color);
            default -> drawCross(context, cx, cy, size, t, gap, color);
        }
    }

    private static void drawDot(DrawContext ctx, int cx, int cy, int size, int color) {
        int r = Math.max(1, size / 2);
        ctx.fill(cx - r, cy - r, cx + r, cy + r, color);
    }

    private static void drawCross(DrawContext ctx, int cx, int cy, int size, int t, int gap, int color) {
        // vertical bar (top + bottom segments, skipping the center gap)
        ctx.fill(cx - t / 2, cy - size, cx + t / 2, cy - gap, color);
        ctx.fill(cx - t / 2, cy + gap, cx + t / 2, cy + size, color);
        // horizontal bar (left + right segments)
        ctx.fill(cx - size, cy - t / 2, cx - gap, cy + t / 2, color);
        ctx.fill(cx + gap, cy - t / 2, cx + size, cy + t / 2, color);
    }

    private static void drawT(DrawContext ctx, int cx, int cy, int size, int t, int gap, int color) {
        // vertical bar below center
        ctx.fill(cx - t / 2, cy + gap, cx + t / 2, cy + size, color);
        // top horizontal bar
        ctx.fill(cx - size, cy - size, cx + size, cy - size + t, color);
    }

    private static void drawX(DrawContext ctx, int cx, int cy, int size, int t, int gap, int color) {
        MatrixStack matrices = ctx.getMatrices();
        matrices.push();
        matrices.translate(cx, cy, 0);
        matrices.multiply(RotationAxis.POSITIVE_Z.rotationDegrees(45));
        // draw a cross centered at origin (then rotated 45° => X shape)
        ctx.fill(-t / 2, -size, t / 2, -gap, color);
        ctx.fill(-t / 2, gap, t / 2, size, color);
        ctx.fill(-size, -t / 2, -gap, t / 2, color);
        ctx.fill(gap, -t / 2, size, t / 2, color);
        matrices.pop();
    }

    private static void drawCircle(DrawContext ctx, int cx, int cy, int size, int t, int color) {
        int radius = Math.max(1, size);
        int steps = Math.max(16, radius * 2);
        double halfT = t / 2.0;
        for (int i = 0; i < steps; i++) {
            double a = (Math.PI * 2.0) * i / steps;
            int px = cx + (int) Math.round(Math.cos(a) * radius);
            int py = cy + (int) Math.round(Math.sin(a) * radius);
            int hw = Math.max(1, (int) Math.round(halfT));
            ctx.fill(px - hw, py - hw, px + hw, py + hw, color);
        }
    }
}
