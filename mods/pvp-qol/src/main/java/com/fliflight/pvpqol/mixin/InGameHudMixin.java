package com.fliflight.pvpqol.mixin;

import com.fliflight.pvpqol.PvPQolClient;
import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.gui.hud.InGameHud;
import net.minecraft.util.Identifier;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(InGameHud.class)
public class InGameHudMixin {
    /**
     * Removes the carved-pumpkin overlay ("pumpkin blur") when enabled in config.
     * The overlay is rendered through renderOverlay with a texture path ending
     * in "pumpkinblur", so we cancel only that specific overlay and leave every
     * other camera overlay (spyglass, etc.) untouched.
     */
    @Inject(method = "renderOverlay", at = @At("HEAD"), cancellable = true)
    private void pvpqol$disablePumpkinBlur(DrawContext context, Identifier texture, float opacity, CallbackInfo ci) {
        if (PvPQolClient.CONFIG.noPumpkinBlur && texture.getPath().contains("pumpkinblur")) {
            ci.cancel();
        }
    }
}
