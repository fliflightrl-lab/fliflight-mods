#!/usr/bin/env python3
"""Whoosh transition SFX (numpy synth)."""
import numpy as np
import wave

SR = 44100
d = 0.8
t = np.linspace(0, d, int(SR*d), False)
rng = np.random.RandomState(5)
noise = rng.randn(len(t))
# highpass (diff) then soften
hp = np.diff(noise, prepend=0)
alpha = 0.35
lp = np.empty_like(hp)
lp[0] = hp[0]
for i in range(1, len(hp)):
    lp[i] = alpha*hp[i] + (1-alpha)*lp[i-1]
# swish envelope (rise then fall)
env = np.sin(np.pi * t / d) ** 1.6
s = lp * env
# slight downward sweep feel: amplitude-modulate a rising sine
sweep = 1.0 + 0.3 * np.sin(2*np.pi*(200 + 900*t/d)*t)
s = s * sweep
s = s / (np.max(np.abs(s)) + 1e-9) * 0.9
# stereo width: small delay on right
left = s
right = np.roll(s, 25)
mix = np.stack([left, right], axis=1)
mix = (mix * 32767).astype(np.int16)
out = "C:/Users/user/fliflight-mods/work/shorts/whoosh.wav"
with wave.open(out, "w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(mix.tobytes())
print("whoosh.wav OK", d, "s")
