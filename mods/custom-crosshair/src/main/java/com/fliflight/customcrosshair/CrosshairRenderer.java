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
        render(ctx, cx, cy, cfg.shape, cfg.getRgbColor(), cfg.size, cfg.thickness, cfg.gap, cfg.dot);
    }

    public static void render(DrawContext ctx, int cx, int cy, String shape, int color, int size, int thickness, int gap, boolean dot) {
        // thickness is at least 1px, and we keep half-thickness at >= 1 so a 1px line is visible.
        int t = Math.max(1, thickness);
        int half = Math.max(1, t / 2);
        switch (shape.toLowerCase()) {
            case "dot" -> drawDot(ctx, cx, cy, size, color);
            case "x" -> drawX(ctx, cx, cy, size, t, gap, color);
            case "circle" -> drawCircle(ctx, cx, cy, size, t, color);
            case "t" -> drawT(ctx, cx, cy, size, t, half, gap, color);
            default -> drawCross(ctx, cx, cy, size, t, half, gap, color);
        }
        if (dot && !"dot".equals(shape.toLowerCase())) {
            drawCenterDot(ctx, cx, cy, half + 1, color);
        }
    }

    /** Filled dot shape. */
    private static void drawDot(DrawContext ctx, int cx, int cy, int size, int color) {
        int r = Math.max(1, size / 2);
        ctx.fill(cx - r, cy - r, cx + r, cy + r, color);
    }

    /** Small center dot (drawn when dot=true in addition to cross/x/t/circle). */
    private static void drawCenterDot(DrawContext ctx, int cx, int cy, int r, int color) {
        ctx.fill(cx - r, cy - r, cx + r + 1, cy + r + 1, color);
    }

    /** Classic 4-arm cross (plus sign). */
    private static void drawCross(DrawContext ctx, int cx, int cy, int size, int t, int half, int gap, int color) {
        ctx.fill(cx - half, cy - size, cx - half + t, cy - gap, color);
        ctx.fill(cx - half, cy + gap, cx - half + t, cy + size, color);
        ctx.fill(cx - size, cy - half, cx - gap, cy - half + t, color);
        ctx.fill(cx + gap, cy - half, cx + size, cy - half + t, color);
    }

    /**
     * T crosshair inspired by real FPS games: a horizontal top bar with a
     * vertical stem dropping from its center. Clean and readable.
     */
    private static void drawT(DrawContext ctx, int cx, int cy, int size, int t, int half, int gap, int color) {
        // Horizontal top bar (full width).
        int top = cy - size;
        ctx.fill(cx - size, top - half, cx + size, top - half + t, color);
        // Vertical stem dropping from the top bar down to the bottom.
        ctx.fill(cx - half, top, cx - half + t, cy + size, color);
    }

    private static void drawX(DrawContext ctx, int cx, int cy, int size, int t, int gap, int color) {
        MatrixStack matrices = ctx.getMatrices();
        int half = Math.max(1, t / 2);
        matrices.push();
        matrices.translate(cx, cy, 0);
        matrices.multiply(RotationAxis.POSITIVE_Z.rotationDegrees(45));
        ctx.fill(-half, -size, -half + t, -gap, color);
        ctx.fill(-half, gap, -half + t, size, color);
        ctx.fill(-size, -half, -gap, -half + t, color);
        ctx.fill(gap, -half, size, -half + t, color);
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
            ctx.fill(px - hw, py - hw, px + hw + 1, py + hw + 1, color);
        }
    }
}
