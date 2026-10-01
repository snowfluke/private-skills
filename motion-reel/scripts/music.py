"""Music choices for the film and reel scores: key, mode, progression, groove preset, sound-effect timbre.

Both score.py files import this module, so each film's music comes from its own DIRECTION.json,
not from a default. There is no default on purpose: two films with the same defaults sound the same.

The "music" block, in timeline.json:
    {"bpm": 92, "root": "F#", "mode": "dorian", "progression": ["i", "IV", "i", "VII"],
     "preset": "broken-beat", "swing": 0.12, "timbre": "glass"}

    python3 music.py --self-test
"""

import sys

NOTES = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6,
         "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
MODES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
}
NUMERALS = ["i", "ii", "iii", "iv", "v", "vi", "vii"]
EXTENSIONS = ("", "7", "9", "sus2", "sus4")

# One bar is 16 steps. Lists are the steps an element plays on. "bass" rows are (step, steps long,
# octave shift). "arp" is a list of scale degrees above the chord root, played every "arp_rate" steps.
PRESETS = {
    "pulse-house": {"kick": [0, 4, 8, 12], "snare": [4, 12], "snare_kind": "clap", "hats": list(range(16)),
                    "open": [2, 6, 10, 14], "bass": [(2, 2, 0), (6, 2, 0), (10, 2, 0), (14, 2, 0)],
                    "lead": "pluck", "arp": [0, 2, 4, 7], "arp_rate": 2, "pad": 1300},
    "broken-beat": {"kick": [0, 7, 10], "snare": [4, 12], "snare_kind": "snare", "hats": list(range(0, 16, 2)) + [15],
                    "open": [6], "bass": [(0, 3, 0), (7, 2, 0), (10, 4, -1)],
                    "lead": "keys", "arp": [0, 4, 2, 5], "arp_rate": 2, "pad": 1000},
    "half-time": {"kick": [0, 10], "snare": [8], "snare_kind": "clap", "hats": list(range(0, 16, 2)) + [13, 14, 15],
                  "open": [], "bass": [(0, 8, 0), (8, 6, -1)],
                  "lead": "saw", "arp": [0, 4, 7], "arp_rate": 4, "pad": 700},
    "motorik": {"kick": [0, 4, 8, 12], "snare": [4, 12], "snare_kind": "rim", "hats": list(range(0, 16, 2)),
                "open": [], "bass": [(s, 2, 0) for s in range(0, 16, 2)],
                "lead": "bell", "arp": [0, 4, 7, 4], "arp_rate": 4, "pad": 1600},
    "minimal-tick": {"kick": [0, 8], "snare": [12], "snare_kind": "rim", "hats": [4, 12],
                     "open": [], "bass": [(0, 6, 0), (8, 6, 0)],
                     "lead": "pluck", "arp": [0, 2, 4, 6, 4, 2], "arp_rate": 2, "pad": 900},
    "ambient-drift": {"kick": [], "snare": [], "snare_kind": "rim", "hats": [],
                      "open": [], "bass": [(0, 16, -1)],
                      "lead": "bell", "arp": [0, 4, 7, 9], "arp_rate": 4, "pad": 2400},
}

# Sound-effect character. Each is a short chain the score applies to its effects bus, so the same
# click or whoosh sounds like glass in one film and like wood in another.
TIMBRES = {
    "glass": "bright and ringing: high-pass, a short metallic ring",
    "wood": "dry and knocky: band-limited, fast decay",
    "analog": "warm: low-pass, soft saturation",
    "digital": "crisp and stepped: bit-reduced, sample-held",
    "soft": "muted and round: gentle low-pass",
    "metal": "hard and resonant: a tuned comb ring",
}

REQUIRED = ("bpm", "root", "mode", "progression", "preset", "timbre")


def check(cfg):
    """Return a list of errors in a music block. Empty means it is usable."""
    if not isinstance(cfg, dict):
        return ["timeline.json needs a \"music\" block with: " + ", ".join(REQUIRED) + " (copy it from DIRECTION.json)"]
    errs = [f"music block misses \"{k}\"" for k in REQUIRED if k not in cfg]
    if errs:
        return errs
    if not (50 <= float(cfg["bpm"]) <= 180):
        errs.append(f"bpm {cfg['bpm']} is outside 50 to 180")
    if cfg["root"] not in NOTES:
        errs.append(f"root {cfg['root']!r} is not one of {', '.join(NOTES)}")
    if cfg["mode"] not in MODES:
        errs.append(f"mode {cfg['mode']!r} is not one of {', '.join(MODES)}")
    if cfg["preset"] not in PRESETS:
        errs.append(f"preset {cfg['preset']!r} is not one of {', '.join(PRESETS)}")
    if cfg["timbre"] not in TIMBRES:
        errs.append(f"timbre {cfg['timbre']!r} is not one of {', '.join(TIMBRES)}")
    prog = cfg["progression"]
    if not isinstance(prog, list) or not 2 <= len(prog) <= 8:
        errs.append("progression is a list of 2 to 8 roman numerals, for example [\"i\", \"VI\", \"III\", \"VII\"]")
    else:
        for p in prog:
            try:
                parse_numeral(p)
            except ValueError as e:
                errs.append(str(e))
    if not 0 <= float(cfg.get("swing", 0)) <= 0.35:
        errs.append("swing is 0 to 0.35")
    return errs


def parse_numeral(p):
    """'VI' -> (5, ''), 'v7' -> (4, '7'), 'IVsus2' -> (3, 'sus2'). Quality comes from the mode, not the case."""
    s = str(p)
    for ext in sorted(EXTENSIONS, key=len, reverse=True):
        if ext and s.endswith(ext):
            s, found = s[: -len(ext)], ext
            break
    else:
        found = ""
    if s.lower() not in NUMERALS:
        raise ValueError(f"progression item {p!r} is not a roman numeral I to VII with an optional 7, 9, sus2 or sus4")
    return NUMERALS.index(s.lower()), found


class Key:
    """Scale notes and chords for one key and mode. MIDI numbers."""

    def __init__(self, root, mode):
        self.root = NOTES[root]
        self.steps = MODES[mode]

    def note(self, degree, octave=4):
        """Scale degree 0..n (may run past 6 into the next octave) as a MIDI note."""
        o, d = divmod(degree, 7)
        return 12 * (octave + 1 + o) + self.root + self.steps[d]

    def chord(self, numeral, octave=4):
        deg, ext = parse_numeral(numeral) if isinstance(numeral, str) else (numeral, "")
        stack = {"": [0, 2, 4], "7": [0, 2, 4, 6], "9": [0, 2, 4, 8], "sus2": [0, 1, 4], "sus4": [0, 3, 4]}[ext]
        return [self.note(deg + s, octave) for s in stack]

    def bass_root(self, numeral, octave=2):
        deg = parse_numeral(numeral)[0] if isinstance(numeral, str) else numeral
        return self.note(deg, octave)


def load(cfg):
    """Check a music block and return (Key, preset dict, bpm, swing, timbre). Exits with every error."""
    errs = check(cfg)
    if errs:
        sys.exit("music: " + "; ".join(errs))
    return Key(cfg["root"], cfg["mode"]), PRESETS[cfg["preset"]], float(cfg["bpm"]), float(cfg.get("swing", 0)), cfg["timbre"]


def apply_timbre(x, name, sr):
    """Colour a mono effects signal. Needs numpy and scipy, like the scores."""
    import numpy as np
    from scipy.signal import butter, lfilter, sosfilt

    def f(kind, freq, sig, order=2):
        return sosfilt(butter(order, freq, kind, fs=sr, output="sos"), sig)

    def comb(sig, hz, fb):
        d = max(1, int(sr / hz))
        a = np.zeros(d + 1)
        a[0], a[d] = 1.0, -fb
        return lfilter([1.0], a, sig)

    if name == "glass":
        y = f("high", 500, x)
        return y + comb(y, 2637, 0.6) * 0.25
    if name == "wood":
        return f("band", [250, 2600], x) * 1.4
    if name == "analog":
        return np.tanh(f("low", 4500, x) * 1.8) / 1.4
    if name == "digital":
        held = np.repeat(x[::4], 4)[: len(x)]
        return np.round(held * 24) / 24
    if name == "soft":
        return f("low", 2500, x)
    if name == "metal":
        return x * 0.6 + comb(f("high", 300, x), 1180, 0.82) * 0.35
    raise ValueError(name)


def self_test():
    good = {"bpm": 96, "root": "F#", "mode": "dorian", "progression": ["i", "IV", "i", "VII"],
            "preset": "broken-beat", "swing": 0.1, "timbre": "glass"}
    assert check(good) == [], check(good)
    for bad in ({**good, "mode": "blues"}, {**good, "progression": ["i", "X"]}, {**good, "bpm": 300},
                {k: v for k, v in good.items() if k != "preset"}, None):
        assert check(bad), f"not caught: {bad}"
    k = Key("C", "major")
    assert k.chord("I") == [60, 64, 67] and k.chord("vi") == [69, 72, 76] and k.chord("V7") == [67, 71, 74, 77]
    m = Key("A", "minor")
    assert m.chord("i") == [69, 72, 76] and m.chord("III") == [72, 76, 79], m.chord("III")
    assert Key("D", "dorian").chord("IV") == [67, 71, 74], "dorian IV must be major"
    assert parse_numeral("IVsus2") == (3, "sus2") and parse_numeral("v7") == (4, "7")
    import numpy as np
    x = np.random.default_rng(1).standard_normal(4800)
    outs = {n: apply_timbre(x, n, 48000) for n in TIMBRES}
    assert all(len(v) == len(x) and np.isfinite(v).all() for v in outs.values())
    names = list(outs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert not np.allclose(outs[names[i]], outs[names[j]]), f"{names[i]} and {names[j]} sound the same"
    print("self-test OK")


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test()
    else:
        sys.exit(__doc__)
