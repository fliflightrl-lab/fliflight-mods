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
 *
 * Layout: controls on the LEFT (scrollable via mouse wheel), live preview on the RIGHT.
 */
public class CrosshairScreen extends Screen {
    private static final int TEXT_COLOR = 0xFFFFFF;

    private final CrosshairConfig config;
    private final Screen parent;

    private final List<String> shapes = List.of("cross", "dot", "x", "circle", "t");
    private final List<String> presetNames = new ArrayList<>(CrosshairPresets.CROSSHAIRS.keySet());
    private final List<String> colorNames = new ArrayList<>(CrosshairPresets.COLORS.keySet());

    /** Scroll offset in pixels (0 = top). */
    private int scroll = 0;
    /** Total content height, used to clamp the scroll range. */
    private int contentHeight = 0;

    private static final int LEFT_MARGIN = 10;
    private static final int CTRL_WIDTH = 160;
    private static final int CTRL_HEIGHT = 20;
    private static final int ROW_GAP = 24;

    public CrosshairScreen(CrosshairConfig config, Screen parent) {
        super(Text.literal("Custom Crosshair"));
        this.config = config;
        this.parent = parent;
    }

    @Override
    protected void init() {
        this.clearChildren();
        int x = LEFT_MARGIN;
        int y = 10 - scroll;

        // Enabled toggle
        this.addDrawableChild(CyclingButtonWidget.onOffBuilder(config.enabled)
                .build(x, y, CTRL_WIDTH, CTRL_HEIGHT, Text.literal("Enabled"), (btn, on) -> {
                    config.enabled = on;
                    config.save();
                }));
        y += ROW_GAP;

        // Shape selector
        int idx = Math.max(0, shapes.indexOf(config.shape));
        this.addDrawableChild(CyclingButtonWidget.<String>builder(s -> Text.literal(s))
                .values(shapes)
                .initially(shapes.get(idx))
                .build(x, y, CTRL_WIDTH, CTRL_HEIGHT, Text.literal("Shape"), (btn, shape) -> {
                    config.shape = shape;
                    config.save();
                }));
        y += ROW_GAP;

        // Size slider
        this.addDrawableChild(new IntSlider(x, y, CTRL_WIDTH, CTRL_HEIGHT, "Size", 1, 30, config.size,
                v -> { config.size = v; config.save(); }));
        y += ROW_GAP;

        // Thickness slider
        this.addDrawableChild(new IntSlider(x, y, CTRL_WIDTH, CTRL_HEIGHT, "Thickness", 1, 8, config.thickness,
                v -> { config.thickness = v; config.save(); }));
        y += ROW_GAP;

        // Gap slider
        this.addDrawableChild(new IntSlider(x, y, CTRL_WIDTH, CTRL_HEIGHT, "Gap", 0, 12, config.gap,
                v -> { config.gap = v; config.save(); }));
        y += ROW_GAP;

        // Per-arm position offsets
        this.addDrawableChild(new IntSlider(x, y, CTRL_WIDTH, CTRL_HEIGHT, "Top Offset", -10, 10, config.topOffset,
                v -> { config.topOffset = v; config.save(); }));
        y += ROW_GAP;
        this.addDrawableChild(new IntSlider(x, y, CTRL_WIDTH, CTRL_HEIGHT, "Bottom Offset", -10, 10, config.bottomOffset,
                v -> { config.bottomOffset = v; config.save(); }));
        y += ROW_GAP;
        this.addDrawableChild(new IntSlider(x, y, CTRL_WIDTH, CTRL_HEIGHT, "Left Offset", -10, 10, config.leftOffset,
                v -> { config.leftOffset = v; config.save(); }));
        y += ROW_GAP;
        this.addDrawableChild(new IntSlider(x, y, CTRL_WIDTH, CTRL_HEIGHT, "Right Offset", -10, 10, config.rightOffset,
                v -> { config.rightOffset = v; config.save(); }));
        y += ROW_GAP;

        // Center dot controls
        this.addDrawableChild(CyclingButtonWidget.onOffBuilder(config.dot)
                .build(x, y, CTRL_WIDTH, CTRL_HEIGHT, Text.literal("Center Dot"), (btn, on) -> {
                    config.dot = on;
                    config.save();
                }));
        y += ROW_GAP;
        this.addDrawableChild(new IntSlider(x, y, CTRL_WIDTH, CTRL_HEIGHT, "Dot Size", 1, 8, config.dotSize,
                v -> { config.dotSize = v; config.save(); }));
        y += ROW_GAP;
        this.addDrawableChild(new IntSlider(x, y, CTRL_WIDTH, CTRL_HEIGHT, "Dot X", -15, 15, config.dotOffsetX,
                v -> { config.dotOffsetX = v; config.save(); }));
        y += ROW_GAP;
        this.addDrawableChild(new IntSlider(x, y, CTRL_WIDTH, CTRL_HEIGHT, "Dot Y", -15, 15, config.dotOffsetY,
                v -> { config.dotOffsetY = v; config.save(); }));
        y += ROW_GAP;

        // Dot color presets (cycling)
        y = addDotColorPresets(x, y);
        y += ROW_GAP;

        // Main color presets (grid of color buttons)
        y = addColorPresets(x, y);
        y += ROW_GAP;

        // RGB sliders
        this.addDrawableChild(new IntSlider(x, y, CTRL_WIDTH, CTRL_HEIGHT, "Red", 0, 255, config.getRed(),
                v -> { config.setRgb(v, config.getGreen(), config.getBlue()); config.save(); }));
        y += ROW_GAP;
        this.addDrawableChild(new IntSlider(x, y, CTRL_WIDTH, CTRL_HEIGHT, "Green", 0, 255, config.getGreen(),
                v -> { config.setRgb(config.getRed(), v, config.getBlue()); config.save(); }));
        y += ROW_GAP;
        this.addDrawableChild(new IntSlider(x, y, CTRL_WIDTH, CTRL_HEIGHT, "Blue", 0, 255, config.getBlue(),
                v -> { config.setRgb(config.getRed(), config.getGreen(), v); config.save(); }));
        y += ROW_GAP;

        // Crosshair presets (grid of preset buttons)
        y = addCrosshairPresets(x, y);
        y += ROW_GAP;

        // Done button
        this.addDrawableChild(ButtonWidget.builder(Text.literal("Done"), b -> this.close())
                .dimensions(x, y, CTRL_WIDTH, CTRL_HEIGHT)
                .build());
        y += ROW_GAP;

        this.contentHeight = y + scroll;
    }

    /** Dot color as a single cycling button over the preset colors. */
    private int addDotColorPresets(int x, int y) {
        int idx = 0;
        for (int i = 0; i < colorNames.size(); i++) {
            if (CrosshairPresets.COLORS.get(colorNames.get(i)) == (config.dotColor | 0xFF000000)) {
                idx = i;
                break;
            }
        }
        this.addDrawableChild(CyclingButtonWidget.<String>builder(s -> Text.literal(s))
                .values(colorNames)
                .initially(colorNames.get(idx))
                .build(x, y, CTRL_WIDTH, CTRL_HEIGHT, Text.literal("Dot Color"), (btn, name) -> {
                    config.dotColor = CrosshairPresets.COLORS.get(name);
                    config.save();
                }));
        return y;
    }

    private int addColorPresets(int x, int y) {
        int total = colorNames.size();
        int cols = 3;
        int rows = (total + cols - 1) / cols;
        int bw = 52;
        int bh = CTRL_HEIGHT;
        int gap = 4;
        for (int i = 0; i < total; i++) {
            int r = i / cols;
            int c = i % cols;
            String name = colorNames.get(i);
            int argb = CrosshairPresets.COLORS.get(name);
            this.addDrawableChild(ButtonWidget.builder(Text.literal(name), b -> {
                        config.color = argb;
                        config.save();
                    })
                    .dimensions(x + c * (bw + gap), y + r * (bh + gap), bw, bh)
                    .build());
        }
        return y + rows * bh + (rows - 1) * gap;
    }

    private int addCrosshairPresets(int x, int y) {
        int total = presetNames.size();
        int cols = 3;
        int rows = (total + cols - 1) / cols;
        int bw = 52;
        int bh = CTRL_HEIGHT;
        int gap = 4;
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
                        config.dot = Integer.parseInt(p[5]) == 1;
                        config.dotSize = p.length > 6 ? Integer.parseInt(p[6]) : 2;
                        config.save();
                        this.init();
                    })
                    .dimensions(x + c * (bw + gap), y + r * (bh + gap), bw, bh)
                    .build());
        }
        return y + rows * bh + (rows - 1) * gap;
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double horizontalAmount, double verticalAmount) {
        int viewport = this.height - 20;
        int maxScroll = Math.max(0, contentHeight - viewport);
        int step = 20;
        if (verticalAmount > 0) {
            scroll = Math.max(0, scroll - step);
        } else if (verticalAmount < 0) {
            scroll = Math.min(maxScroll, scroll + step);
        }
        this.init();
        return true;
    }

    @Override
    public void render(DrawContext context, int mouseX, int mouseY, float delta) {
        super.render(context, mouseX, mouseY, delta);
        // Live preview on the RIGHT side, vertically centered.
        int cx = this.width - 80;
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
