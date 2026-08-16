package com.fliflight.pvphud.mixin;

import com.fliflight.pvphud.CpsTracker;
import net.minecraft.client.MinecraftClient;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(MinecraftClient.class)
public class MinecraftClientMixin {
    /**
     * Counts a left click (attack). doAttack() is called once per attack key press.
     */
    @Inject(method = "doAttack", at = @At("HEAD"))
    private void pvphud$countLeftClick(CallbackInfoReturnable<Boolean> cir) {
        CpsTracker.onLeftClick();
    }

    /**
     * Counts a right click (use). doItemUse() is called once per use key press.
     */
    @Inject(method = "doItemUse", at = @At("HEAD"))
    private void pvphud$countRightClick(CallbackInfo ci) {
        CpsTracker.onRightClick();
    }
}
