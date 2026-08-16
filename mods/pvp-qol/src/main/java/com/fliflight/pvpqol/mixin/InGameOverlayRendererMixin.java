package com.fliflight.pvpqol.mixin;

import com.fliflight.pvpqol.PvPQolClient;
import net.minecraft.client.gui.hud.InGameOverlayRenderer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

@Mixin(InGameOverlayRenderer.class)
public class InGameOverlayRendererMixin {
    /**
     * Lowers the fire overlay (the flame you see while burning) by increasing
     * the downward Y offset of the fire quad. Vanilla uses -0.3F; a larger
     * negative offset pushes the flame further down so it appears lower/shorter.
     */
    @ModifyArg(
            method = "renderFireOverlay",
            at = @At(
                    value = "INVOKE",
                    target = "Lnet/minecraft/client/util/math/MatrixStack;translate(FFF)V"
            ),
            index = 1
    )
    private static float pvpqol$lowerFireOverlay(float y) {
        if (PvPQolClient.CONFIG.lowerFireEnabled) {
            return y - PvPQolClient.CONFIG.fireLowerOffset;
        }
        return y;
    }
}
