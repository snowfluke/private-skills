"""Synthesize the reel score: the film's own music plus the timeline's sound cues.

Picture and sound share src/timeline.json, so every cue lands on the beat its motion does.
Deterministic: seeded noise, no samples. The reel loops: everything is rendered with a two-bar
tail, and the tail is folded back onto the start, so reverb and ringing notes cross the loop point.

The music comes from the "music" block in src/timeline.json, copied from DIRECTION.json (see
music.py next to this file). Its bpm must equal the timeline's bpm. Each section carries an
"energy" role that sets the arrangement: intro, build, drop, break, logo, outro. An optional
"gate": [from_beat, to_beat] silences the music for a breath; the effects stay.

    uv run --with numpy --with scipy python audio/score.py  ->  public/score.wav (loudness -14 LUFS)
    python3 audio/score.py --self-test
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import music as M  # noqa: E402  (music.py sits next to this file)

ENERGY = ("intro", "build", "drop", "break", "logo", "outro")


def self_test():
    """Two reels with different music blocks must differ; the same block twice must match; length is frame-exact."""
    import tempfile
    blocks = [{"bpm": 118, "root": "E", "mode": "phrygian", "progression": ["i", "II", "i", "VII"],
               "preset": "half-time", "swing": 0.0, "timbre": "metal"},
              {"bpm": 118, "root": "G", "mode": "mixolydian", "progression": ["I", "VII", "IV", "I"],
               "preset": "motorik", "swing": 0.08, "timbre": "soft"}]
    outs = []
    with tempfile.TemporaryDirectory() as d:
        for n, block in enumerate(blocks + blocks[:1]):
            root = os.path.join(d, str(n))
            os.makedirs(os.path.join(root, "src"))
            os.makedirs(os.path.join(root, "public"))
            tl = {"bpm": 118, "fps": 30, "beats": 32, "music": block,
                  "sections": [{"id": "a", "start": 0, "len": 8, "energy": "intro"},
                               {"id": "b", "start": 8, "len": 16, "energy": "drop"},
                               {"id": "c", "start": 24, "len": 8, "energy": "logo"}],
                  "cues": [{"beat": 0, "sfx": "hit"}, {"beat": 8, "sfx": "pop"}, {"beat": 24, "sfx": "impact"}]}
            json.dump(tl, open(os.path.join(root, "src", "timeline.json"), "w"))
            subprocess.run([sys.executable, os.path.abspath(__file__)], env={**os.environ, "SCORE_ROOT": root, "SCORE_RAW": "1"},
                           check=True, capture_output=True)
            outs.append(open(os.path.join(root, "public", "score.wav"), "rb").read())
    assert outs[0] != outs[1], "two different music blocks produced the same score"
    assert outs[0] == outs[2], "the same music block produced two different scores"
    frames = round(32 * 60 / 118 * 30)
    assert (len(outs[0]) - 44) // 4 == round(frames / 30 * 48000), "the loop must last exactly the picture's frames"
    print("self-test OK")


if __name__ == "__main__" and sys.argv[1:] == ["--self-test"]:
    self_test()
    sys.exit(0)

import numpy as np  # noqa: E402
from scipy.io import wavfile  # noqa: E402
from scipy.signal import butter, sosfilt  # noqa: E402

ROOT = os.environ.get("SCORE_ROOT") or os.path.dirname(HERE)
TL = json.load(open(os.path.join(ROOT, "src", "timeline.json")))
MCFG = TL.get("music")
KEY, PRESET, _BPM, SWING, TIMBRE = M.load(MCFG)
if float(MCFG["bpm"]) != float(TL["bpm"]):
    sys.exit(f"music bpm {MCFG['bpm']} differs from the timeline bpm {TL['bpm']}; the picture and the score must share one tempo")
for sct in TL["sections"]:
    if sct.get("energy") not in ENERGY:
        sys.exit(f"section {sct['id']!r} needs \"energy\": one of {', '.join(ENERGY)}")
SR = 48000
# The picture is a whole number of frames, so the loop length is too; the beat stretches by <0.04%
# so picture and sound wrap together.
LEN = round(TL["beats"] * 60 / TL["bpm"] * TL["fps"]) / TL["fps"]
BEAT = LEN / TL["beats"]
LOOP_N = int(round(SR * LEN))
TAIL = 8 * BEAT
N = LOOP_N + int(SR * TAIL)
SEED = sum(json.dumps(MCFG, sort_keys=True).encode())
rng = np.random.default_rng(SEED)

drums = np.zeros((N, 2))
synth = np.zeros((N, 2))
sfx = np.zeros((N, 2))


def sec(b):
    return b * BEAT


def t_axis(d):
    return np.arange(int(d * SR)) / SR


def lp(x, f, o=2):
    return sosfilt(butter(o, min(f, SR / 2 - 100), "low", fs=SR, output="sos"), x)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, o=2):
    return sosfilt(butter(o, [lo, min(hi, SR / 2 - 100)], "band", fs=SR, output="sos"), x)


def lpenv(x, lo, hi, e):
    """Filter sweep from hi down to lo, as a crossfade shaped by e (1 = bright)."""
    return lp(x, hi) * e + lp(x, lo) * (1 - e)


def env(n, a, d, s=0.0, r=None):
    an, dn = max(1, int(a * SR)), max(1, int(d * SR))
    e = np.zeros(n)
    e[: min(an, n)] = np.linspace(0, 1, an)[: min(an, n)]
    if n > an:
        m = min(dn, n - an)
        e[an : an + m] = np.linspace(1, s, dn)[:m]
        e[an + m :] = s
    if r:
        rn = min(int(r * SR), n)
        e[n - rn :] *= np.linspace(1, 0, rn)
    return e


def place(bus, x, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N or i < 0:
        return
    x = x[: N - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    bus[i : i + len(x), 0] += x * gain * l * 1.4142
    bus[i : i + len(x), 1] += x * gain * r * 1.4142


def hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def saw(f, t):
    return 2 * ((t * f) % 1.0) - 1


def sweep(f0, f1, d, curve=1.0):
    t = t_axis(d)
    f = f0 + (f1 - f0) * np.linspace(0, 1, len(t)) ** curve
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def noise(d):
    return rng.standard_normal(int(d * SR))


# ---------------------------------------------------------------- instruments

def kick():
    t = t_axis(0.32)
    body = np.sin(2 * np.pi * np.cumsum(46 + 120 * np.exp(-t * 38)) / SR) * np.exp(-t * 8)
    click = hp(noise(0.32), 3000) * np.exp(-t * 400) * 0.35
    return np.tanh((body + click) * 1.6)


def clap():
    x = np.zeros(int(0.25 * SR))
    for k, off in enumerate((0, 0.009, 0.019)):
        b = bp(noise(0.2), 900, 3200) * np.exp(-t_axis(0.2) * (60 if k < 2 else 16))
        place_arr(x, b, off)
    return x * 0.9


def place_arr(dst, src, at):
    i = int(at * SR)
    n = min(len(src), len(dst) - i)
    dst[i : i + n] += src[:n]


def hat(open_=False):
    d = 0.22 if open_ else 0.045
    return hp(noise(d), 7500) * np.exp(-t_axis(d) * (14 if open_ else 90)) * 0.6


def snare():
    t = t_axis(0.18)
    return bp(noise(0.18), 1200, 7000) * np.exp(-t * 24) * 0.7 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.5


def bass(n, d):
    t = t_axis(d)
    x = saw(hz(n), t) * 0.6 + np.sin(2 * np.pi * hz(n) * t) * 0.8
    return lpenv(x, 380, 1280, np.exp(-t * 18)) * env(len(t), 0.004, d, 0.85, 0.03)


def pluck(n, d=0.2, bright=1.0):
    t = t_axis(d)
    x = saw(hz(n), t) + saw(hz(n) * 1.004, t)
    return lpenv(x * 0.5, 900, 900 + 5200 * bright, np.exp(-t * 22)) * env(len(t), 0.002, d, 0.0)


def pad(notes, d, bright=1600):
    t = t_axis(d)
    x = sum(saw(hz(n + det), t + rng.random() * 0.03) for n in notes for det in (-0.1, 0.0, 0.11))
    return lp(x / (3 * len(notes)), bright) * env(len(t), 0.3, 0.2, 0.9, 0.5)


def supersaw(n, d):
    t = t_axis(d)
    x = sum(saw(hz(n + det), t + rng.random() * 0.01) for det in (-0.18, -0.07, 0.0, 0.08, 0.19))
    return lpenv(x / 5, 900, 5100, np.exp(-t * 3)) * env(len(t), 0.004, d, 0.6, 0.05)


def bell(f, d=1.4, idx=2.0):
    t = t_axis(d)
    return np.sin(2 * np.pi * f * t + np.sin(2 * np.pi * f * 3.5 * t) * idx * np.exp(-t * 5)) * np.exp(-t * 3.2)


def riser(d):
    x = hp(noise(d), 1500) * np.linspace(0, 1, int(d * SR)) ** 2.5
    return lp(x, 12000) * 0.8 + sweep(200, 1400, d, 2.0) * np.linspace(0, 1, int(d * SR)) ** 2 * 0.25


# ---------------------------------------------------------------- sound effects (in the reel's key)

# Tonic, third, fifth, seventh and octave of the key, around MIDI octave 5. The names keep the
# roles, not the pitches.
D5, F5, A5, C6, D6 = (KEY.note(d, 5) for d in (0, 2, 4, 6, 7))
LOW, HIGH = KEY.note(0, 4), KEY.note(7, 5)


def fx_whoosh(d=0.45, up=True):
    x = noise(d)
    out = np.zeros(len(x))
    seg = 480
    for s in range(0, len(x), seg):
        p = s / len(x)
        c = 350 * (10 ** (p if up else 1 - p))
        out[s : s + seg] = bp(x[max(0, s - 1500) : s + seg], c * 0.7, c * 1.5)[-len(out[s : s + seg]) :]
    return out * np.sin(np.pi * np.linspace(0, 1, len(x))) ** 1.2


def fx_suck():
    d = BEAT
    x = lp(noise(d), 5000) * np.linspace(0, 1, int(d * SR)) ** 3
    return x + sweep(80, 400, d, 2) * np.linspace(0, 1, int(d * SR)) ** 3 * 0.4


def fx_hit():
    t = t_axis(0.5)
    return np.sin(2 * np.pi * np.cumsum(50 + 110 * np.exp(-t * 26)) / SR) * np.exp(-t * 8) + bp(noise(0.5), 800, 6000) * np.exp(-t * 30) * 0.5


def fx_impact():
    t = t_axis(2.4)
    boom = np.sin(2 * np.pi * np.cumsum(32 + 80 * np.exp(-t * 7)) / SR) * np.exp(-t * 2)
    air = lp(noise(2.4), 3000) * np.exp(-t * 3) * 0.5
    ring = np.zeros(len(t))
    ring[: int(2.0 * SR)] = bell(hz(D6), 2.0, 1.4) * 0.5
    return boom + air + ring


def fx_blip(n, d=0.06, lvl=0.5):
    t = t_axis(d)
    return np.sin(2 * np.pi * hz(n) * t) * env(len(t), 0.002, d) * lvl


def fx_glitch():
    x = np.zeros(int(0.35 * SR))
    for k in range(9):
        seg = bp(noise(0.03), 400 + rng.random() * 4000, 9000) * (0.4 + rng.random() * 0.6)
        seg = np.round(seg * 6) / 6
        place_arr(x, seg, k * 0.037)
    return x * 0.8


def fx_slam():
    t = t_axis(0.25)
    return np.sin(2 * np.pi * np.cumsum(70 + 140 * np.exp(-t * 40)) / SR) * np.exp(-t * 16) + bp(noise(0.25), 1500, 6000) * np.exp(-t * 60) * 0.5


def fx_pop(n=A5):
    t = t_axis(0.08)
    return np.sin(2 * np.pi * np.cumsum(np.linspace(hz(n - 12), hz(n), len(t))) / SR) * np.exp(-t * 40) * 0.7


def fx_popcluster():
    x = np.zeros(int(1.2 * SR))
    for k in range(14):
        place_arr(x, fx_pop([D5, F5, A5, C6, D6][k % 5]) * 0.6, k * 0.06 + rng.random() * 0.02)
    return x


def fx_flip():
    t = t_axis(0.12)
    return bp(noise(0.12), 1800, 5000) * np.exp(-t * 60) * 0.6 + np.sin(2 * np.pi * 900 * t) * np.exp(-t * 50) * 0.3 + fx_whoosh(0.12) * 0.3


def fx_thud():
    t = t_axis(0.4)
    return np.sin(2 * np.pi * np.cumsum(55 + 50 * np.exp(-t * 20)) / SR) * np.exp(-t * 9)


def fx_draw():
    d = 0.6
    return sweep(hz(LOW), hz(HIGH), d, 1.5) * env(int(d * SR), 0.05, d, 0.0) * 0.4 + fx_whoosh(d) * 0.4


def fx_zap():
    return sweep(2400, 300, 0.18, 0.5) * np.exp(-t_axis(0.18) * 14) * 0.5


def fx_success():
    return np.concatenate([fx_blip(A5, 0.08), fx_blip(D6, 0.22)])


def fx_shimmer():
    x = np.zeros(int(2.6 * SR))
    for k, n in enumerate([D6, A5 + 12, F5 + 12, D6 + 12, A5 + 24]):
        place_arr(x, bell(hz(n), 2.0, 1.0) * 0.35, k * 0.09)
    return x


def fx_sparkle():
    x = np.zeros(int(2.2 * SR))
    for k in range(12):
        place_arr(x, bell(hz([D6, F5 + 12, A5 + 12, C6 + 12][k % 4] + 12 * (k // 8)), 1.2, 0.8) * 0.25, k * 0.045)
    return x


def fx_boing():
    t = t_axis(0.6)
    f = hz(LOW) * (1 + 0.5 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 5))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4) * 0.6


def fx_sweep():
    d = 2 * BEAT
    return bp(noise(d), 1500, 5000) * np.sin(np.pi * np.linspace(0, 1, int(d * SR))) * 0.5


def fx_echo():
    x = np.zeros(int(1.6 * SR))
    for k in range(8):
        place_arr(x, fx_blip(D6, 0.05, 0.7) * 0.85 ** k, k * BEAT * 0.25)
    return x


def fx_blips():
    x = np.zeros(int(0.9 * SR))
    for k, n in enumerate([D5, F5, A5, C6, D6, F5 + 12, A5 + 12, D6 + 12]):
        place_arr(x, fx_blip(n, 0.05), k * 0.05)
    return x


def fx_splash():
    t = t_axis(1.0)
    x = lp(noise(1.0), 2500) * np.exp(-t * 5) * 0.8
    for k in range(10):
        place_arr(x, fx_pop(D5 + int(rng.random() * 12)) * 0.25, 0.1 + rng.random() * 0.7)
    return x


def fx_chime():
    return bell(hz(D6), 1.4, 1.2) * 0.5 + bell(hz(A5 + 12), 1.4, 0.8) * 0.25


def fx_key():
    t = t_axis(0.035)
    return bp(noise(0.035), 1500 + rng.random() * 1500, 7000) * np.exp(-t * 150) * 0.5


FX = {"whoosh": (fx_whoosh, 0.4), "click": (lambda: fx_blip(96, 0.02, 0.8), 0.5), "drag": (lambda: fx_whoosh(0.3) * 0.6, 0.3),
      "zip": (lambda: sweep(300, 3000, 0.35, 2) * np.exp(-t_axis(0.35) * 4) * 0.5, 0.45), "suck": (fx_suck, 0.5), "hit": (fx_hit, 0.8),
      "glitch": (fx_glitch, 0.45), "slam": (fx_slam, 0.6), "swish": (lambda: fx_whoosh(0.25), 0.35), "impact": (fx_impact, 1.0),
      "popcluster": (fx_popcluster, 0.45), "flip": (fx_flip, 0.5), "thud": (fx_thud, 0.6), "pop": (fx_pop, 0.5), "draw": (fx_draw, 0.45),
      "zap": (fx_zap, 0.4), "success": (fx_success, 0.5), "shimmer": (fx_shimmer, 0.5), "sparkle": (fx_sparkle, 0.55),
      "boing": (fx_boing, 0.5), "sweep": (fx_sweep, 0.35), "echo": (fx_echo, 0.4), "blips": (fx_blips, 0.45), "splash": (fx_splash, 0.6),
      "chime": (fx_chime, 0.55), "tick": (lambda: fx_blip(98, 0.025, 0.7), 0.35)}

for cue in TL["cues"]:
    at, name = sec(cue["beat"]), cue["sfx"]
    pan = float(np.sin(at * 1.9) * 0.3)
    if name.startswith("type:"):
        for k in range(int(name.split(":")[1])):
            place(sfx, fx_key(), at + k * BEAT / 4, 0.45, pan)
    else:
        fn, gain = FX[name]
        place(sfx, fn(), at, gain, pan)

# ---------------------------------------------------------------- music
# Every bar takes its arrangement from the energy role of the section it falls in. Harmony,
# groove and lead come from the music block; the lead motif comes from a seed of that block, so
# two reels in the same key still get different melodies.

PROG = MCFG["progression"]
SNARE = {"clap": clap, "snare": snare, "rim": lambda: fx_blip(96, 0.03, 0.7)}[PRESET["snare_kind"]]
STEP = 0.25  # beats
MOTIF = [(0, 0.75), (0.75, 0.75), (1.5, 0.5), (2, 0.75), (2.75, 0.5), (3.25, 0.75)]
MOTIF_DEG = [int(d) for d in rng.choice([0, 2, 4, 5, 7, 9], size=len(MOTIF))]
kicks = []

# energy -> drum density, arp level, lead on, pad brightness factor
ROLE = {"intro": (0.3, 0.25, False, 0.6), "build": (0.6, 0.5, False, 0.9), "drop": (1.0, 0.9, True, 1.2),
        "break": (0.15, 0.6, False, 1.4), "logo": (0.6, 0.7, False, 1.6), "outro": (0.3, 0.4, False, 0.8)}


def role_at(beat):
    for sct in TL["sections"]:
        if sct["start"] <= beat < sct["start"] + sct["len"]:
            return sct["energy"]
    return "outro"


def at_step(bar, s):
    return sec(bar * 4 + s * STEP + (SWING * STEP if s % 2 else 0.0))


def drums_bar(bar, density):
    if density >= 0.3:
        for s in PRESET["kick"]:
            place(drums, kick(), at_step(bar, s), 0.9)
            kicks.append(at_step(bar, s))
    if density >= 0.6:
        for s in PRESET["snare"]:
            place(drums, SNARE(), at_step(bar, s), 0.55, 0.05)
    if density >= 0.15:
        for s in PRESET["hats"]:
            place(drums, hat(), at_step(bar, s), 0.16 if s % 2 else 0.24, -0.25)
    if density >= 0.9:
        for s in PRESET["open"]:
            place(drums, hat(True), at_step(bar, s), 0.2, 0.25)


def lead(n, d):
    kind = PRESET["lead"]
    if kind == "saw":
        return supersaw(n, d)
    if kind == "pluck":
        return pluck(n, d, 0.8)
    return bell(hz(n), d * 2.0, 1.4 if kind == "bell" else 0.8) * 0.6


def harmony_bar(bar, arp, bright, with_lead):
    at = sec(bar * 4)
    numeral = PROG[bar % len(PROG)]
    deg = M.parse_numeral(numeral)[0]
    for s, steps, octave in PRESET["bass"]:
        place(synth, bass(KEY.bass_root(numeral, 2) + 12 * octave, sec(steps * STEP * 0.95)), at_step(bar, s), 0.45)
    if arp:
        rate = PRESET["arp_rate"]
        for k, s in enumerate(range(0, 16, rate)):
            n = KEY.note(deg + PRESET["arp"][k % len(PRESET["arp"])], 5)
            place(synth, pluck(n, sec(rate * STEP), arp), at_step(bar, s), 0.2, np.sin(k * 1.1) * 0.5)
    place(synth, pad(KEY.chord(numeral, 4), sec(4) + 0.3, PRESET["pad"] * bright), at, 0.26)
    if with_lead:
        for (off, dur), d in zip(MOTIF, MOTIF_DEG):
            place(synth, lead(KEY.note(d, 5), sec(dur)), at + sec(off), 0.28)


def roll(start, length, lvl=0.5):
    for k in range(int(length * 6)):
        place(drums, snare(), sec(start + length * (k / (length * 6)) ** 0.85), 0.06 + lvl * k / (length * 6))


BARS = int(np.ceil(TL["beats"] / 4))
for bar in range(BARS):
    density, arp, with_lead, bright = ROLE[role_at(bar * 4)]
    drums_bar(bar, density)
    harmony_bar(bar, arp, bright, with_lead)

# Section changes: a riser into every drop, and a hit with a ringing chord on every logo.
for sct in TL["sections"]:
    if sct["energy"] == "drop" and sct["start"] >= 2:
        place(synth, riser(sec(2)), sec(sct["start"] - 2), 0.45)
    if sct["energy"] == "logo":
        place(synth, pad(KEY.chord("i9", 3) + [KEY.note(0, 5)], sec(8) + 0.6, PRESET["pad"] * 1.8), sec(sct["start"]), 0.5)
        place(synth, bass(KEY.note(0, 2), sec(4)), sec(sct["start"]), 0.45)
        for k, d in enumerate([0, 2, 4, 7, 9, 11]):
            place(synth, bell(hz(KEY.note(d, 5)), 2.2, 1.0), sec(sct["start"]) + k * 0.09, 0.22, -0.5 + k * 0.2)

# The loop: a riser and a roll resolve onto beat 0 of the next pass.
place(synth, riser(sec(2)), sec(TL["beats"] - 2), 0.5)
roll(TL["beats"] - 1.5, 1.5, 0.5)
GATE = tuple(TL["gate"]) if "gate" in TL else None

# ---------------------------------------------------------------- mix


def reverb(x, amount):
    out = x.copy()
    for d, g in ((0.031, 0.5), (0.047, 0.45), (0.069, 0.4), (0.101, 0.33), (0.149, 0.27), (0.221, 0.2), (0.313, 0.14)):
        n = int(d * SR)
        tail = np.zeros_like(x)
        tail[n:] = x[:-n] * g
        out += lp(tail, 5000) * amount
    return out


duck = np.ones(N)
for k in kicks:
    i = int(k * SR)
    seg = min(int(BEAT * SR), N - i)
    if seg > 0:
        duck[i : i + seg] = np.minimum(duck[i : i + seg], 1 - 0.65 * np.exp(-np.arange(seg) / SR * 11))

gate = np.ones(N)
if GATE:
    g0, g1, fade = int(sec(GATE[0]) * SR), int(sec(GATE[1]) * SR), int(0.03 * SR)
    gate[g0:g1] = 0
    gate[g0 - fade:g0] = np.linspace(1, 0, fade)
    gate[g1:g1 + fade] = np.linspace(0, 1, fade)
drums *= gate[:, None]
synth *= gate[:, None]
synth = np.stack([hp(reverb(synth[:, c], 0.25), 35) * duck for c in range(2)], axis=1)
drums = np.stack([hp(drums[:, c], 25) for c in range(2)], axis=1)
sfx = np.stack([lp(reverb(M.apply_timbre(sfx[:, c], TIMBRE, SR), 0.12), 12000) for c in range(2)], axis=1)
mix = drums * 0.8 + synth * 0.7 + sfx * 0.9
# The loop: fold the tail onto the start. No fade in, no fade out.
loop = mix[:LOOP_N].copy()
tail = mix[LOOP_N:]
loop[: len(tail)] += tail
loop = np.tanh(loop / np.max(np.abs(loop)) * 1.5) / np.tanh(1.5) * 0.9
raw = os.path.join(ROOT, "public", "score-raw.wav")
wavfile.write(raw, SR, (loop * 32767).astype(np.int16))
if os.environ.get("SCORE_RAW"):
    os.replace(raw, os.path.join(ROOT, "public", "score.wav"))
    sys.exit(0)
# Two-pass loudnorm in linear mode: one static gain, so nothing ramps across the loop point.
probe = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.2:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
m = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
flt = (f"loudnorm=I=-14:TP=-1.2:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
       f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", flt, "-ar", str(SR), os.path.join(ROOT, "public", "score.wav")], check=True)
os.remove(raw)
print("seconds", round(LOOP_N / SR, 3), "cues", len(TL["cues"]))
