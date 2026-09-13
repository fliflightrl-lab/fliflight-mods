#!/usr/bin/env python3
"""Generate an energetic phonk-style beat (original, royalty-free) as WAV."""
import numpy as np
import wave

SR = 44100
BPM = 146
BEAT = 60 / BPM
DUR = 30.0

def kick(d=0.55):
    t = np.linspace(0, d, int(SR*d), False)
    f = 150 * np.exp(-t*20) + 44
    ph = 2*np.pi*np.cumsum(f)/SR
    return np.sin(ph) * np.exp(-t*8)

def clap(d=0.22):
    t = np.linspace(0, d, int(SR*d), False)
    n = np.random.RandomState(7).randn(len(t))
    s = n * np.exp(-t*28)
    s += 0.4*np.sin(2*np.pi*200*t)*np.exp(-t*22)
    return s*0.7

def hat(d=0.06, decay=55):
    t = np.linspace(0, d, int(SR*d), False)
    return np.random.randn(len(t)) * np.exp(-t*decay) * 0.35

def cowbell(f, d=0.22):
    t = np.linspace(0, d, int(SR*d), False)
    s = (np.sin(2*np.pi*f*t) + 0.55*np.sin(2*np.pi*f*1.49*t) + 0.3*np.sin(2*np.pi*f*2.01*t))
    return s * np.exp(-t*14) * 0.42

def bass(f, d=BEAT*0.95):
    t = np.linspace(0, d, int(SR*d), False)
    s = np.sin(2*np.pi*f*t)
    s += 0.3*np.sin(2*np.pi*f*2*t)
    return s * np.exp(-t*3) * 0.55

def place(buf, snd, t, gain=1.0):
    i = int(t*SR)
    j = min(i + len(snd), len(buf))
    if i < len(buf):
        buf[i:j] += snd[:j-i] * gain

# note -> freq helper (A minor scale)
NOTE = {"A2":110.0,"C3":130.81,"D3":146.83,"E3":164.81,"G3":196.0,
        "A3":220.0,"C4":261.63,"D4":293.66,"E4":329.63,"G4":392.0,"A4":440.0}

# dark phonk riff (cowbell), 8 steps per bar, 2 bars
riff = ["A4",0,"C5" if "C5" in NOTE else "C4","A4",0,"G4","E4","G4",
        "A4",0,"C5" if "C5" in NOTE else "C4","A4","E4","G4","A4",0]
NOTE["C5"] = 523.25
riff = ["A4",0,"C5","A4",0,"G4","E4","G4","A4",0,"C5","A4","E4","G4","A4",0]
# bassline (root notes), 2 bars
bassline = ["A2","A2","A2","A2","F2" if "F2" in NOTE else "A2","F2" if "F2" in NOTE else "A2","G2" if "G2" in NOTE else "G3","G2" if "G2" in NOTE else "G3"]
NOTE["F2"]=87.31; NOTE["G2"]=98.0
bassline = ["A2","A2","A2","A2","F2","F2","G2","G2"]

N = int(SR*DUR)
L = np.zeros(N); R = np.zeros(N)
total_beats = int(DUR / BEAT)
step = BEAT / 2  # 8th note

for b in range(total_beats):
    t = b * BEAT
    # kick every beat
    place(L, kick(), t); place(R, kick(), t)
    # clap on beats 1 and 3 (0-indexed even? -> beats 2 & 4 -> odd index)
    if b % 2 == 1:
        place(L, clap(), t); place(R, clap(), t)
    # hats on 8ths (offset half beat), accent on offbeat
    ht = t + step/2
    place(L, hat(), ht, 0.9); place(R, hat(), ht, 0.9)
    place(L, hat(), ht, 0.9); place(R, hat(), ht, 0.9)
    # cowbell riff: 16 steps over 2 bars -> step index = b % 16
    ri = b % 16
    if riff[ri]:
        place(L, cowbell(NOTE[riff[ri]]), t); place(R, cowbell(NOTE[riff[ri]]), t)
    # bass every beat (sustained)
    bi = b % 8
    place(L, bass(NOTE[bassline[bi]]), t); place(R, bass(NOTE[bassline[bi]]), t)

# normalize + light stereo width
mix = np.stack([L, R], axis=1)
peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * 0.85
mix = (mix * 32767).astype(np.int16)

out = "C:/Users/user/fliflight-mods/work/shorts/music_phonk.wav"
with wave.open(out, "w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(mix.tobytes())
print("music:", out, f"{DUR}s")
