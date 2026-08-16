package com.fliflight.customcrosshair.mixin;

import com.fliflight.customcrosshair.CrosshairModClient;
import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.gui.hud.InGameHud;
import net.minecraft.client.render.RenderTickCounter;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(InGameHud.class)
public class InGameHudMixin {
    /**
     * Hides the vanilla crosshair when our custom crosshair is enabled.
     * Our own crosshair is drawn via HudRenderCallback (see CrosshairModClient).
     */
    @Inject(method = "renderCrosshair", at = @At("HEAD"), cancellable = true)
    private void customcrosshair$hideVanillaCrosshair(DrawContext context, RenderTickCounter tickCounter, CallbackInfo ci) {
        if (CrosshairModClient.CONFIG.enabled) {
            ci.cancel();
        }
    }
}
