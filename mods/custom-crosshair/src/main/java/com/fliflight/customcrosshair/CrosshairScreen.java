package com.fliflight.customcrosshair;

import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.gui.screen.Screen;
import net.minecraft.client.gui.widget.ButtonWidget;
import net.minecraft.client.gui.widget.CyclingButtonWidget;
import net.minecraft.client.gui.widget.SliderWidget;
import net.minecraft.text.Text;

import java.util.ArrayList;
import java.util.List;
import java.util.function.IntConsumer;

/**
 * In-game configuration screen for the custom crosshair.
 * Opened with the configured key binding (default: C).
 */
public class CrosshairScreen extends Screen {
    private static final int TEXT_COLOR = 0xFFFFFF;

    private final CrosshairConfig config;
    private final Screen parent;

    private final List<String> shapes = List.of("cross", "dot", "x", "circle", "t");
    private final List<String> presetNames = new ArrayList<>(CrosshairPresets.CROSSHAIRS.keySet());
    private final List<String> colorNames = new ArrayList<>(CrosshairPresets.COLORS.keySet());

    public CrosshairScreen(CrosshairConfig config, Screen parent) {
        super(Text.literal("Custom Crosshair"));
        this.config = config;
        this.parent = parent;
    }

    @Override
    protected void init() {
        int w = this.width;
        int centerX = w / 2;
        int btnW = 150;
        int btnX = centerX - btnW / 2;
        int y = 20;

        // Enabled toggle
        this.addDrawableChild(CyclingButtonWidget.onOffBuilder(config.enabled)
                .build(centerX - 75, y, 150, 20, Text.literal("Enabled"), (btn, on) -> {
                    config.enabled = on;
                    config.save();
                }));
        y += 24;

        // Shape selector
        int idx = Math.max(0, shapes.indexOf(config.shape));
        this.addDrawableChild(CyclingButtonWidget.<String>builder(s -> Text.literal(s))
                .values(shapes)
                .initially(shapes.get(idx))
                .build(centerX - 75, y, 150, 20, Text.literal("Shape"), (btn, shape) -> {
                    config.shape = shape;
                    config.save();
                }));
        y += 24;

        // Size slider
        this.addDrawableChild(new IntSlider(btnX, y, btnW, 20, "Size", 1, 30, config.size,
                v -> { config.size = v; config.save(); }));
        y += 24;

        // Thickness slider
        this.addDrawableChild(new IntSlider(btnX, y, btnW, 20, "Thickness", 1, 8, config.thickness,
                v -> { config.thickness = v; config.save(); }));
        y += 24;

        // Gap slider
        this.addDrawableChild(new IntSlider(btnX, y, btnW, 20, "Gap", 0, 12, config.gap,
                v -> { config.gap = v; config.save(); }));
        y += 26;

        // Color presets (row of color names)
        y = addColorPresets(centerX, y);
        y += 8;

        // RGB sliders
        this.addDrawableChild(new IntSlider(btnX, y, btnW, 20, "Red", 0, 255, config.getRed(),
                v -> { config.setRgb(v, config.getGreen(), config.getBlue()); config.save(); }));
        y += 24;
        this.addDrawableChild(new IntSlider(btnX, y, btnW, 20, "Green", 0, 255, config.getGreen(),
                v -> { config.setRgb(config.getRed(), v, config.getBlue()); config.save(); }));
        y += 24;
        this.addDrawableChild(new IntSlider(btnX, y, btnW, 20, "Blue", 0, 255, config.getBlue(),
                v -> { config.setRgb(config.getRed(), config.getGreen(), v); config.save(); }));
        y += 28;

        // Crosshair presets
        y = addCrosshairPresets(centerX, y);
        y += 12;

        // Done button
        this.addDrawableChild(ButtonWidget.builder(Text.literal("Done"), b -> this.close())
                .dimensions(centerX - 100, y, 200, 20)
                .build());
    }

    private int addColorPresets(int centerX, int y) {
        int total = colorNames.size();
        int cols = Math.min(total, 4);
        int rows = (total + cols - 1) / cols;
        int bw = 70;
        int bh = 20;
        int gap = 6;
        int gridW = cols * bw + (cols - 1) * gap;
        int startX = centerX - gridW / 2;
        for (int i = 0; i < total; i++) {
            int r = i / cols;
            int c = i % cols;
            String name = colorNames.get(i);
            int argb = CrosshairPresets.COLORS.get(name);
            this.addDrawableChild(ButtonWidget.builder(Text.literal(name), b -> {
                        config.color = argb;
                        config.save();
                    })
                    .dimensions(startX + c * (bw + gap), y + r * (bh + gap), bw, bh)
                    .build());
        }
        return y + rows * bh + (rows - 1) * gap;
    }

    private int addCrosshairPresets(int centerX, int y) {
        int total = presetNames.size();
        int cols = 3;
        int rows = (total + cols - 1) / cols;
        int bw = 70;
        int bh = 20;
        int gap = 6;
        int gridW = cols * bw + (cols - 1) * gap;
        int startX = centerX - gridW / 2;
        for (int i = 0; i < total; i++) {
            int r = i / cols;
            int c = i % cols;
            String name = presetNames.get(i);
            this.addDrawableChild(ButtonWidget.builder(Text.literal(name), b -> {
                        String[] p = CrosshairPresets.CROSSHAIRS.get(name);
                        config.shape = p[0];
                        config.color = (int) Long.parseLong(p[1].substring(2), 16);
                        config.size = Integer.parseInt(p[2]);
                        config.thickness = Integer.parseInt(p[3]);
                        config.gap = Integer.parseInt(p[4]);
                        config.save();
                        this.clearChildren();
                        this.init();
                    })
                    .dimensions(startX + c * (bw + gap), y + r * (bh + gap), bw, bh)
                    .build());
        }
        return y + rows * bh + (rows - 1) * gap;
    }

    @Override
    public void render(DrawContext context, int mouseX, int mouseY, float delta) {
        super.render(context, mouseX, mouseY, delta);
        // Live preview of the crosshair, centered.
        int cx = this.width / 2;
        int cy = this.height / 2;
        context.drawCenteredTextWithShadow(this.textRenderer, "Preview", cx, cy - 40, TEXT_COLOR);
        CrosshairRenderer.render(context, cx, cy, config);
    }

    @Override
    public boolean shouldPause() {
        return false;
    }

    @Override
    public void close() {
        config.save();
        if (this.client != null) {
            this.client.setScreen(parent);
        }
    }

    /** Simple integer slider. */
    private static final class IntSlider extends SliderWidget {
        private final String label;
        private final int min;
        private final int max;
        private final IntConsumer onChange;
        private int current;

        IntSlider(int x, int y, int width, int height, String label, int min, int max, int initial, IntConsumer onChange) {
            super(x, y, width, height, Text.empty(), (initial - min) / (double) (max - min));
            this.label = label;
            this.min = min;
            this.max = max;
            this.current = initial;
            this.onChange = onChange;
            updateMessage();
        }

        @Override
        protected void updateMessage() {
            setMessage(Text.literal(label + ": " + current));
        }

        @Override
        protected void applyValue() {
            current = (int) Math.round(min + this.value * (max - min));
            onChange.accept(current);
            updateMessage();
        }
    }
}
