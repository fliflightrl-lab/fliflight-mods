package com.fliflight.customcrosshair;

import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.util.math.MatrixStack;
import net.minecraft.util.math.RotationAxis;

/**
 * Shared crosshair drawing logic, used both by the in-game HUD overlay
 * and by the config screen's live preview.
 *
 * All elements are laid out with a single centering helper so the bars and the
 * center dot stay perfectly aligned with one another.
 */
public final class CrosshairRenderer {
    private CrosshairRenderer() {}

    public static void render(DrawContext ctx, int cx, int cy, CrosshairConfig cfg) {
        int color = cfg.getRgbColor();
        int t = Math.max(1, cfg.thickness);

        switch (cfg.shape.toLowerCase()) {
            case "dot" -> drawDotShape(ctx, cx, cy, cfg.size, color);
            case "x" -> drawX(ctx, cx, cy, cfg.size, t, cfg.gap, color, cfg.topOffset, cfg.bottomOffset, cfg.leftOffset, cfg.rightOffset);
            case "circle" -> drawCircle(ctx, cx, cy, cfg.size, t, color);
            case "t" -> drawT(ctx, cx, cy, cfg.size, t, cfg.gap, color, cfg.topOffset, cfg.leftOffset);
            default -> drawCross(ctx, cx, cy, cfg.size, t, cfg.gap, color, cfg.topOffset, cfg.bottomOffset, cfg.leftOffset, cfg.rightOffset);
        }

        if (cfg.dot && !"dot".equals(cfg.shape.toLowerCase())) {
            drawCenterDot(ctx, cx + cfg.dotOffsetX, cy + cfg.dotOffsetY, cfg.dotSize, cfg.getDotRgbColor());
        }
    }

    /**
     * Fills a rectangle of size (w,h) centered on (cx,cy). All shapes use this
     * same convention so elements stay mutually aligned.
     */
    private static void centeredFill(DrawContext ctx, int cx, int cy, int w, int h, int color) {
        int x1 = cx - w / 2;
        int y1 = cy - h / 2;
        ctx.fill(x1, y1, x1 + w, y1 + h, color);
    }

    /** Horizontal bar from x1 to x2, thickness t, vertically centered on cy. */
    private static void hBar(DrawContext ctx, int x1, int x2, int cy, int t, int color) {
        int y1 = cy - t / 2;
        ctx.fill(x1, y1, x2, y1 + t, color);
    }

    /** Vertical bar from y1 to y2, thickness t, horizontally centered on cx. */
    private static void vBar(DrawContext ctx, int cx, int y1, int y2, int t, int color) {
        int x1 = cx - t / 2;
        ctx.fill(x1, y1, x1 + t, y2, color);
    }

    /** Full-crosshair-as-a-dot shape. */
    private static void drawDotShape(DrawContext ctx, int cx, int cy, int size, int color) {
        int d = Math.max(1, size);
        centeredFill(ctx, cx, cy, d, d, color);
    }

    /** Center dot added on top of other shapes. dotSize is the radius. */
    private static void drawCenterDot(DrawContext ctx, int cx, int cy, int radius, int color) {
        int d = Math.max(1, radius) * 2;
        centeredFill(ctx, cx, cy, d, d, color);
    }

    /**
     * Classic 4-arm cross (plus sign). Per-arm offsets shift each arm along its
     * own axis (positive = further from the center).
     */
    private static void drawCross(DrawContext ctx, int cx, int cy, int size, int t, int gap, int color,
                                  int top, int bottom, int left, int right) {
        vBar(ctx, cx, cy - size, cy - gap - top, t, color);
        vBar(ctx, cx, cy + gap + bottom, cy + size, t, color);
        hBar(ctx, cx - size, cx - gap - left, cy, t, color);
        hBar(ctx, cx + gap + right, cx + size, cy, t, color);
    }

    /**
     * T crosshair inspired by real FPS games: a horizontal top bar with a
     * vertical stem dropping from its center.
     */
    private static void drawT(DrawContext ctx, int cx, int cy, int size, int t, int gap, int color,
                              int top, int left) {
        int barY = cy - size - top;
        hBar(ctx, cx - size, cx + size, barY, t, color);
        vBar(ctx, cx + left, barY, cy + size, t, color);
    }

    private static void drawX(DrawContext ctx, int cx, int cy, int size, int t, int gap, int color,
                              int top, int bottom, int left, int right) {
        MatrixStack matrices = ctx.getMatrices();
        matrices.push();
        matrices.translate(cx, cy, 0);
        matrices.multiply(RotationAxis.POSITIVE_Z.rotationDegrees(45));
        vBar(ctx, 0, -size, -gap - top, t, color);
        vBar(ctx, 0, gap + bottom, size, t, color);
        hBar(ctx, -size, -gap - left, 0, t, color);
        hBar(ctx, gap + right, size, 0, t, color);
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
            centeredFill(ctx, px, py, Math.max(1, t), Math.max(1, t), color);
        }
    }
}
