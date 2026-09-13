#!/usr/bin/env python3
"""Boom-bap FR old-school beat (numpy synth, no credit cost)."""
import numpy as np
import wave

SR = 44100
BPM = 90
BEAT = 60 / BPM
DUR = 30.0

def kick(d=0.35):
    t = np.linspace(0, d, int(SR*d), False)
    f = 120*np.exp(-t*25) + 48
    ph = 2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-t*9)*0.9

def snare(d=0.25):
    t = np.linspace(0, d, int(SR*d), False)
    n = np.random.RandomState(3).randn(len(t))
    s = n*np.exp(-t*26)
    s += 0.5*np.sin(2*np.pi*185*t)*np.exp(-t*22)
    return s*0.7

def hat(d=0.05):
    t = np.linspace(0, d, int(SR*d), False)
    # highpass-ish: use noise with fast decay
    return np.random.randn(len(t))*np.exp(-t*50)*0.32

def piano(f, d=1.2):
    t = np.linspace(0, d, int(SR*d), False)
    s = (np.sin(2*np.pi*f*t) + 0.4*np.sin(2*np.pi*f*2*t) + 0.15*np.sin(2*np.pi*f*3*t))
    return s*np.exp(-t*3.2)

def bass(f, d=BEAT*1.8):
    t = np.linspace(0, d, int(SR*d), False)
    s = np.sin(2*np.pi*f*t) + 0.25*np.sin(2*np.pi*f*2*t)
    return s*np.exp(-t*2.5)*0.5

def place(buf, snd, t, gain=1.0):
    i = int(t*SR); j = min(i+len(snd), len(buf))
    if i < len(buf):
        buf[i:j] += snd[:j-i]*gain

# jazz chords (A minor): Am7, Dm7, E7, Am7
CHORDS = [
    [110.0, 130.81, 164.81, 196.00],   # Am7
    [146.83, 174.61, 220.00, 261.63],  # Dm7
    [164.81, 207.65, 246.94, 293.66],  # E7
    [110.0, 130.81, 164.81, 196.00],   # Am7
]
ROOTS = [110.0, 146.83, 164.81, 110.0]

N = int(SR*DUR)
L = np.zeros(N); R = np.zeros(N)
total_beats = int(DUR / BEAT)
swing = 0.12  # swing factor on off-beat 8ths

for b in range(total_beats):
    t = b*BEAT
    # boom-bap: kick on beats 0 & 2, snare on 1 & 3
    if b % 4 in (0, 2):
        place(L, kick(), t); place(R, kick(), t)
    if b % 4 in (1, 3):
        place(L, snare(), t); place(R, snare(), t)
    # hats on 8ths with swing
    place(L, hat(), t, 0.9); place(R, hat(), t, 0.9)
    ht = t + BEAT/2 + (swing if b % 2 == 0 else -swing)
    place(L, hat(), ht, 0.7); place(R, hat(), ht, 0.7)
    # piano chord stab at bar start (beat 0 of each 4-beat bar)
    if b % 4 == 0:
        chord = CHORDS[(b//4) % 4]
        for f in chord:
            place(L, piano(f), t, 0.5); place(R, piano(f), t+0.01, 0.5)
        # bass root
        place(L, bass(ROOTS[(b//4) % 4]), t, 0.8); place(R, bass(ROOTS[(b//4) % 4]), t, 0.8)

# dusty vinyl: gentle noise floor + slight lowpass via moving average
mix = np.stack([L, R], axis=1)
noise = np.random.RandomState(1).randn(N, 2) * 0.004
mix += noise
peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * 0.85
mix = (mix*32767).astype(np.int16)

out = "C:/Users/user/fliflight-mods/work/shorts/music/boombap_fr.wav"
with wave.open(out, "w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(mix.tobytes())
print("boombap_fr.wav OK")
