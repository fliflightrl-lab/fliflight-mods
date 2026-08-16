package com.fliflight.customcrosshair;

import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.util.math.MatrixStack;
import net.minecraft.util.math.RotationAxis;

/**
 * Shared crosshair drawing logic, used both by the in-game HUD overlay
 * and by the config screen's live preview.
 */
public final class CrosshairRenderer {
    private CrosshairRenderer() {}

    public static void render(DrawContext ctx, int cx, int cy, CrosshairConfig cfg) {
        render(ctx, cx, cy, cfg.shape, cfg.getRgbColor(), cfg.size, cfg.thickness, cfg.gap);
    }

    public static void render(DrawContext ctx, int cx, int cy, String shape, int color, int size, int thickness, int gap) {
        int t = Math.max(1, thickness);
        switch (shape.toLowerCase()) {
            case "dot" -> drawDot(ctx, cx, cy, size, color);
            case "x" -> drawX(ctx, cx, cy, size, t, gap, color);
            case "circle" -> drawCircle(ctx, cx, cy, size, t, color);
            case "t" -> drawT(ctx, cx, cy, size, t, gap, color);
            default -> drawCross(ctx, cx, cy, size, t, gap, color);
        }
    }

    private static void drawDot(DrawContext ctx, int cx, int cy, int size, int color) {
        int r = Math.max(1, size / 2);
        ctx.fill(cx - r, cy - r, cx + r, cy + r, color);
    }

    private static void drawCross(DrawContext ctx, int cx, int cy, int size, int t, int gap, int color) {
        ctx.fill(cx - t / 2, cy - size, cx + t / 2, cy - gap, color);
        ctx.fill(cx - t / 2, cy + gap, cx + t / 2, cy + size, color);
        ctx.fill(cx - size, cy - t / 2, cx - gap, cy + t / 2, color);
        ctx.fill(cx + gap, cy - t / 2, cx + size, cy + t / 2, color);
    }

    private static void drawT(DrawContext ctx, int cx, int cy, int size, int t, int gap, int color) {
        ctx.fill(cx - t / 2, cy + gap, cx + t / 2, cy + size, color);
        ctx.fill(cx - size, cy - size, cx + size, cy - size + t, color);
    }

    private static void drawX(DrawContext ctx, int cx, int cy, int size, int t, int gap, int color) {
        MatrixStack matrices = ctx.getMatrices();
        matrices.push();
        matrices.translate(cx, cy, 0);
        matrices.multiply(RotationAxis.POSITIVE_Z.rotationDegrees(45));
        ctx.fill(-t / 2, -size, t / 2, -gap, color);
        ctx.fill(-t / 2, gap, t / 2, size, color);
        ctx.fill(-size, -t / 2, -gap, t / 2, color);
        ctx.fill(gap, -t / 2, size, t / 2, color);
        matrices.pop();
    }

    private static void drawCircle(DrawContext ctx, int cx, int cy, int size, int t, int color) {
        int radius = Math.max(1, size);
        int steps = Math.max(16, radius * 2);
        int hw = Math.max(1, t / 2);
        for (int i = 0; i < steps; i++) {
            double a = (Math.PI * 2.0) * i / steps;
            int px = cx + (int) Math.round(Math.cos(a) * radius);
            int py = cy + (int) Math.round(Math.sin(a) * radius);
            ctx.fill(px - hw, py - hw, px + hw, py + hw, color);
        }
    }
}
