#!/usr/bin/env python3
"""Check a film's DIRECTION.json: every choice traced to the product, and different from earlier films.

    direction.py check DIRECTION.json --repo <app repo> [--storyboard STORYBOARD.md]
    direction.py record DIRECTION.json          after delivery, so the next film differs from this one
    direction.py --self-test

The format is in ../references/direction.md. A copy of this file lives in the other video skill's
scripts/ folder; each skill installs on its own, so change both.

History: the bundled ../history/seed.jsonl plus the user's own file at
$VIDEO_DIRECTIONS (default ~/.local/share/video-directions/history.jsonl). A new direction may
share at most MAX_SHARED of the compared choices with any earlier film.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import music as M  # noqa: E402

MAX_SHARED = 2
ARCS = ("journey", "before-after", "scale-reveal", "build-from-nothing", "race", "day-in-the-life",
        "question-answer", "catalog")
FINALES = ("collapse-to-mark", "montage-accelerate", "zoom-out-reveal", "split-merge", "type-lockup",
           "mosaic-resolve", "trace-the-path", "loop-to-start")
# The finales each arc allows (references/arcs.md). A loop always ends on loop-to-start.
ARC_FINALES = {"journey": ("trace-the-path", "zoom-out-reveal"), "before-after": ("split-merge", "type-lockup"),
               "scale-reveal": ("zoom-out-reveal", "mosaic-resolve"), "build-from-nothing": ("collapse-to-mark", "type-lockup"),
               "race": ("split-merge", "type-lockup"), "day-in-the-life": ("loop-to-start", "trace-the-path"),
               "question-answer": ("type-lockup", "zoom-out-reveal"), "catalog": ("montage-accelerate", "mosaic-resolve")}
FORMATS = ("film", "loop")
CHOSEN = ("arc", "hero_motion", "music")  # each lists the options it rejected
LAYOUTS = ("split-caption", "lower-third", "full-bleed-type", "corner-index", "center-stack", "no-caption")
EVIDENCED = ("product", "mechanic", "audience", "tone")
REASONED = ("metaphor", "arc", "hero_motion", "finale", "layout")
# Signatures of the first film these skills made. A new film never reuses them.
FORBIDDEN = ("node rain", "and many more")
OLD_PILLARS = ("speed", "flexibility", "inspection", "iteration", "visual abstraction")
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
SEED = os.path.join(HERE, "..", "history", "seed.jsonl")
USER = os.environ.get("VIDEO_DIRECTIONS") or os.path.expanduser("~/.local/share/video-directions/history.jsonl")


def source(ev, repo):
    """(ok, text): text is the cited file's content, "" for a URL, None when the citation is broken."""
    if not isinstance(ev, str) or not ev.strip():
        return False, None
    if ev.startswith(("http://", "https://")):
        return True, ""
    path, _, anchor = ev.partition("#")
    if repo is None:
        return True, None
    full = os.path.join(repo, path.strip())
    if not os.path.isfile(full):
        return False, None
    text = open(full, encoding="utf-8", errors="replace").read()
    m = re.match(r"L(\d+)(?:-L?(\d+))?$", anchor.strip()) if anchor else None
    if anchor and (not m or int(m.group(2) or m.group(1)) > text.count("\n") + 1):
        return False, None
    return True, text


def evidence_ok(ev, repo):
    return source(ev, repo)[0]


def contrast(a, b):
    def lum(h):
        c = [v / 255 for v in rgb(h)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def words(text):
    return {w for w in re.findall(r"[a-z]{4,}", str(text).lower())}


def storyboard_errors(path):
    """The hand-off table: every row names what is on screen and the object it hands to the next row."""
    lines = open(path, encoding="utf-8").read().splitlines()
    head = next((i for i, l in enumerate(lines) if l.startswith("|") and "on screen" in l.lower()
                 and re.search(r"hand-?off", l.lower())), None)
    if head is None:
        return ["storyboard: needs a table whose header has an \"On screen\" column and a \"Hand-off\" column"]
    cols = [c.strip().lower() for c in lines[head].strip().strip("|").split("|")]
    on, ho = next(i for i, c in enumerate(cols) if "on screen" in c), next(i for i, c in enumerate(cols) if re.search(r"hand-?off", c))
    errs, rows = [], 0
    for n, l in enumerate(lines[head + 2:], head + 3):
        if not l.startswith("|"):
            break
        rows += 1
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        for i, name in ((on, "On screen"), (ho, "Hand-off")):
            if i >= len(cells) or cells[i].lower() in ("", "-", "tbd", "none", "n/a"):
                errs.append(f"storyboard line {n}: the {name} cell is empty; a row without it has no place in the film")
    return errs if rows else ["storyboard: the hand-off table has no rows"]


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def shared(a, b):
    """The compared choices two directions have in common."""
    same = []
    get = lambda d, *ks: _dig(d, ks)
    for name, keys in (("arc", ("arc", "value")), ("finale", ("finale", "value")), ("hero motion", ("hero_motion", "family")),
                       ("layout", ("layout", "value")), ("groove preset", ("music", "preset")), ("sfx timbre", ("music", "timbre"))):
        if get(a, *keys) is not None and get(a, *keys) == get(b, *keys):
            same.append(name)
    if get(a, "music", "root") == get(b, "music", "root") and get(a, "music", "mode") == get(b, "music", "mode") and get(a, "music", "root"):
        same.append("key")
    ba, bb = get(a, "music", "bpm"), get(b, "music", "bpm")
    if ba and bb and abs(float(ba) - float(bb)) <= 6:
        same.append("tempo")
    ca, cb = get(a, "palette", "canvas"), get(b, "palette", "canvas")
    if ca and cb and HEX.match(ca) and HEX.match(cb) and sum((x - y) ** 2 for x, y in zip(rgb(ca), rgb(cb))) ** 0.5 < 40:
        same.append("canvas colour")
    return same


def _dig(d, ks):
    for k in ks:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def history():
    out = []
    for p in (SEED, USER):
        if os.path.exists(p):
            out += [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    return out


def check(d, repo=None, storyboard=None, past=None):
    errs = []
    for k in EVIDENCED:
        if not isinstance(d.get(k), dict):
            errs.append(f"{k}: missing")
        elif not evidence_ok(d[k].get("evidence"), repo):
            errs.append(f"{k}: evidence must be an existing file in the app repo (path, or path#L12 within the file) "
                        f"or a URL, got {d[k].get('evidence')!r}")
    tone = [str(w).lower() for w in (_dig(d, ("tone", "words")) or [])]
    ok, text = source(_dig(d, ("tone", "evidence")), repo)
    if ok and text is not None:
        where = text.lower() if text else str(_dig(d, ("tone", "quote")) or "").lower()
        if text == "" and len(where.split()) < 6:
            errs.append("tone: a URL source needs a \"quote\" of at least six words copied from the page")
        missing = [w for w in tone if w not in where]
        if missing:
            errs.append(f"tone: {', '.join(missing)} not found in the cited source; quote the product's own words")
    facts = words(_dig(d, ("mechanic", "verb"))) | words(_dig(d, ("mechanic", "what"))) | words(" ".join(tone)) \
        | words(_dig(d, ("metaphor", "value")))
    for k in REASONED + ("music",):
        why = str(_dig(d, (k, "why")) or "")
        ws = why.lower().split()
        if len(ws) < 6 or max((ws.count(w) for w in ws), default=0) > 3:
            errs.append(f"{k}: give a \"why\" of at least six different words")
        elif k != "metaphor" and not (words(why) & facts):
            errs.append(f"{k}: the \"why\" must name the mechanic, a tone word or the world it serves")
    for k in CHOSEN:
        rejected = _dig(d, (k, "rejected")) or []
        if len([r for r in rejected if len(str(r).split()) >= 3]) < 2:
            errs.append(f"{k}: list at least two options you considered and rejected, each with its reason, in \"rejected\"")
    if _dig(d, ("mechanic", "verb")) in (None, ""):
        errs.append("mechanic: name the physical verb the product performs, for example scan, match, route, grow")
    if len(_dig(d, ("tone", "words")) or []) < 2:
        errs.append("tone: quote at least two words from the README or the landing page")
    for k, allowed in (("arc", ARCS), ("finale", FINALES), ("layout", LAYOUTS)):
        v = _dig(d, (k, "value"))
        if v not in allowed:
            errs.append(f"{k}: {v!r} is not one of {', '.join(allowed)}")
    fmt, arc, fin = d.get("format"), _dig(d, ("arc", "value")), _dig(d, ("finale", "value"))
    if fmt not in FORMATS:
        errs.append(f"format: \"film\" for a launch film, \"loop\" for a looping reel, got {fmt!r}")
    elif fmt == "loop" and fin != "loop-to-start":
        errs.append("finale: a loop ends on loop-to-start, so its last frame is its first")
    elif fmt == "film" and arc in ARC_FINALES and fin not in ARC_FINALES[arc]:
        errs.append(f"finale: the {arc} arc ends on {' or '.join(ARC_FINALES[arc])}")
    if not _dig(d, ("hero_motion", "family")) or not _dig(d, ("hero_motion", "value")):
        errs.append("hero_motion: needs a \"family\" (a short kebab-case name) and a \"value\" describing the motion")
    pal = d.get("palette") or {}
    if not evidence_ok(pal.get("evidence"), repo):
        errs.append("palette: evidence for the brand colours must be a file in the app repo or a URL")
    for name, need in (("brand", 1), ("invented", 3)):
        cols = pal.get(name) or []
        if len(cols) < need or not all(isinstance(c, str) and HEX.match(c) for c in cols):
            errs.append(f"palette.{name}: at least {need} colours as #rrggbb")
    if not isinstance(pal.get("canvas"), str) or not HEX.match(pal.get("canvas", "")):
        errs.append("palette.canvas: the film background as #rrggbb")
    elif not isinstance(pal.get("ink"), str) or not HEX.match(pal.get("ink", "")):
        errs.append("palette.ink: the text colour on the canvas as #rrggbb")
    elif contrast(pal["ink"], pal["canvas"]) < 4.5:
        errs.append(f"palette.ink on palette.canvas is {contrast(pal['ink'], pal['canvas']):.1f}:1; text needs 4.5:1 or more")
    ok, text = source(pal.get("evidence"), repo)
    if ok and text:
        low = text.lower()
        for c in pal.get("brand") or []:
            if isinstance(c, str) and c.lower() not in low:
                errs.append(f"palette.brand: {c} is not in the cited file; brand colours come from the repo")
    errs += [f"music: {e}" for e in M.check(d.get("music"))]
    if isinstance(d.get("music"), dict) and len(str(d["music"].get("why", "")).split()) < 6:
        errs.append("music: give a \"why\" of at least six words that ties tempo and mode to the tone")
    if storyboard:
        errs += storyboard_errors(storyboard)
    text = json.dumps(d).lower() + (open(storyboard, encoding="utf-8").read().lower() if storyboard else "")
    for phrase in FORBIDDEN:
        if phrase in text:
            errs.append(f"\"{phrase}\" is the first film's signature; invent this product's own beat")
    if sum(re.search(rf"\b{w}\b", text) is not None for w in OLD_PILLARS) >= 3:
        errs.append("three or more of the first film's pillar words (speed, flexibility, inspection, iteration, visual "
                    "abstraction); take this product's own pillars from its README or landing page")
    for past_d in (history() if past is None else past):
        same = shared(d, past_d)
        if len(same) > MAX_SHARED:
            errs.append(f"too close to the earlier film {past_d.get('label', '?')!r}: shares {', '.join(same)}. "
                        f"Change all but {MAX_SHARED} of them.")
    return errs


def record(d, label):
    os.makedirs(os.path.dirname(USER), exist_ok=True)
    keep = {k: d[k] for k in ("arc", "finale", "hero_motion", "layout", "palette", "music") if k in d}
    with open(USER, "a", encoding="utf-8") as f:
        f.write(json.dumps({"label": label, **keep}) + "\n")


def example():
    return {
        "product": {"name": "Ledgerline", "evidence": "README.md#L1"},
        "mechanic": {"verb": "scan", "what": "reads text out of receipt photos", "evidence": "README.md#L5"},
        "audience": {"value": "finance teams closing the month", "evidence": "README.md#L9"},
        "tone": {"words": ["private", "instant"], "evidence": "README.md#L2"},
        "format": "film",
        "metaphor": {"value": "a darkroom where text develops out of the photo", "why": "the product pulls text out of an image, like a print developing"},
        "arc": {"value": "journey", "why": "one receipt travels from a crumpled photo to a booked ledger line",
                "rejected": ["race: no slower rival to beat", "catalog: the product does one thing well"]},
        "hero_motion": {"family": "scan-reveal", "value": "a light bar sweeps down and leaves typed text behind it",
                        "why": "the scan is the product's mechanic, so it carries every cut",
                        "rejected": ["fold: says compress, not read", "zipper: says match, not read"]},
        "finale": {"value": "zoom-out-reveal", "why": "the one receipt becomes a month of receipts filed in a grid"},
        "layout": {"value": "lower-third", "why": "the photo needs the full frame width while it develops"},
        "palette": {"brand": ["#3b5bdb"], "invented": ["#1a1410", "#e8d5b0", "#c2410c"], "canvas": "#1a1410", "ink": "#e8d5b0",
                    "evidence": "src/theme.css#L1"},
        "music": {"bpm": 88, "root": "Eb", "mode": "dorian", "progression": ["i", "IV", "VII", "i"], "preset": "minimal-tick",
                  "swing": 0.1, "timbre": "analog", "why": "unhurried and exact, so private feels safe and instant feels easy",
                  "rejected": ["pulse-house at 124: too loud for private", "ambient-drift: hides the instant result"]},
    }


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as repo:
        os.makedirs(os.path.join(repo, "src"))
        open(os.path.join(repo, "README.md"), "w").write("# Ledgerline\nPrivate, instant receipt reading.\n" + "x\n" * 10)
        open(os.path.join(repo, "src/theme.css"), "w").write(":root { --brand: #3B5BDB; }\n")
        good = example()
        assert check(good, repo, past=[]) == [], check(good, repo, past=[])
        twin = json.loads(json.dumps(good))
        twin["label"] = "earlier"
        assert any("too close" in e for e in check(good, repo, past=[twin])), "a copy of an earlier film must fail"
        near = json.loads(json.dumps(twin))
        near["music"].update({"bpm": 140, "root": "A", "mode": "lydian", "preset": "pulse-house", "timbre": "glass"})
        near["palette"]["canvas"] = "#f0f0f0"
        near["arc"]["value"] = "race"
        near["layout"]["value"] = "center-stack"
        assert check(good, repo, past=[near]) == [], "sharing two choices must pass"
        bad = {
            "made-up evidence file": ("product", {"name": "x", "evidence": "docs/nowhere.md"}),
            "no why": ("arc", {"value": "journey", "why": "nice"}),
            "unknown arc": ("arc", {"value": "epic", "why": "one receipt travels from a photo to a ledger"}),
            "one tone word": ("tone", {"words": ["fast"], "evidence": "README.md"}),
            "bad music": ("music", {**good["music"], "mode": "blues"}),
            "old signature": ("finale", {"value": "trace-the-path", "why": "then a node rain of every receipt the scan reads"}),
            "anchor past the end": ("product", {"name": "x", "evidence": "README.md#L9999"}),
            "tone word not in source": ("tone", {"words": ["zesty", "luminous"], "evidence": "README.md"}),
            "URL tone without quote": ("tone", {"words": ["private", "instant"], "evidence": "https://example.com"}),
            "brand colour not in repo": ("palette", {**good["palette"], "brand": ["#123456"]}),
            "padded why": ("arc", {**good["arc"], "why": "because because because because because because"}),
            "why unrelated to the product": ("finale", {"value": "trace-the-path", "why": "it looks really nice and modern overall"}),
            "no rejected options": ("music", {k: v for k, v in good["music"].items() if k != "rejected"}),
            "finale outside the arc": ("finale", {"value": "split-merge", "why": "the receipt scan splits and merges into the mark"}),
            "loop without loop finale": ("format", "loop"),
            "unreadable ink": ("palette", {**good["palette"], "ink": "#2a2018"}),
        }
        for name, (k, v) in bad.items():
            assert check({**good, k: v}, repo, past=[]), f"self-test: '{name}' was not caught"
        sb = os.path.join(repo, "STORYBOARD.md")
        head = "| Time | Scene | On screen | Hand-off | Sound |\n|---|---|---|---|---|\n"
        open(sb, "w").write(head + "| 0-4 | a | the photo | the scan bar | whoosh |\n| 4-8 | b | the text | the mark | hit |\n")
        assert check(good, repo, storyboard=sb, past=[]) == [], check(good, repo, storyboard=sb, past=[])
        open(sb, "w").write(head + "| 0-4 | a | the photo | - | whoosh |\n")
        assert check(good, repo, storyboard=sb, past=[]), "a row with no hand-off must fail"
        open(sb, "w").write(head + "| 0-4 | Speed | x | y | z |\n| 4-8 | Flexibility | x | y | z |\n| 8-12 | Inspection | x | y | z |\n")
        assert check(good, repo, storyboard=sb, past=[]), "the old pillar set in a storyboard must fail"
    seed = [json.loads(l) for l in open(SEED, encoding="utf-8") if l.strip()]
    assert seed, "history/seed.jsonl must hold the first film"
    print("self-test OK")


def main(argv):
    if argv[:1] == ["--self-test"]:
        return self_test()
    import argparse
    ap = argparse.ArgumentParser(prog="direction.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("direction")
    c.add_argument("--repo", required=True, help="the app repository the film is about")
    c.add_argument("--storyboard")
    r = sub.add_parser("record")
    r.add_argument("direction")
    r.add_argument("--label", required=True, help="a short name for this film, for example the product and the date")
    a = ap.parse_args(argv)
    d = json.load(open(a.direction, encoding="utf-8"))
    if a.cmd == "record":
        record(d, a.label)
        print(f"recorded {a.label!r} in {USER}")
        return
    errs = check(d, a.repo, a.storyboard)
    if errs:
        print("\n".join(f"- {e}" for e in errs), file=sys.stderr)
        sys.exit(1)
    print("direction OK")


if __name__ == "__main__":
    main(sys.argv[1:])
