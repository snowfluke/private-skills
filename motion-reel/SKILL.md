---
name: motion-reel
description: Build a short, looping, music-driven motion-graphics reel (15 to 45 s) that shows a product through motion, with no voiceover and no subtitles, for an exhibition screen, a booth, a lobby display, a showreel or a social loop. Reads the repository, the README and the landing page, then invents a direction for this product alone, covering its world, its pillars, a signature hand-off motion, the palette, and a score with its own tempo, key and groove. Uses Remotion with a beat-grid timeline, hand-off transitions between every section, and a seamless picture-and-sound loop, and checks that the reel differs from earlier ones. Use it for requests like "30-second reel for the exhibition", "looping motion graphics for our booth", "a brand reel at 120 BPM", "make it loop seamlessly", or revisions to a reel made this way. Use `app-launch-video` for a narrated launch film and `brag-slim` for a one-off 20 s share clip.
compatibility: Needs Node with npx, Remotion (a Remotion project, or copy the template), ffmpeg, and Python 3 with numpy and scipy (uv works). The ax CLI helps read the landing page.
---

# Motion reel

A loop that a passer-by can join at any second. Every section shows a real
part of the product. Every cut hands one object to the next section. The last
frame is the first frame, and the music wraps with it.

Two reels from this skill must never look or sound alike. Each one starts
from its own `DIRECTION.json`, checked against the product and against earlier
films. There is no default tempo, palette, pillar list or music.

Paths below are relative to this skill's folder. Find it first, then call each
script by its absolute path.

## 0. Prerequisites

| Need | Check | Fix |
|---|---|---|
| Node, npx | `node -v` | Node 20 or later |
| Remotion project | `npx remotion versions` in the project | `npx create-video@latest`, then copy `assets/template/*` into `src/` |
| ffmpeg | `ffmpeg -version` | `brew install ffmpeg` |
| numpy, scipy | `uv --version` | `uv run --with numpy --with scipy python ...` |

## 1. Discover and direct

Read the README, the docs index, the landing page (fetch it with `ax`, or
`curl`), the main screen and the theme. Then write `DIRECTION.json`. The format and
the choices (world, hero motion, palette, music) are in
`references/direction.md`; take the arc from the reel's own shape: one idea per
section, building to the mark. Check it:

```bash
python3 <skill>/scripts/direction.py check DIRECTION.json --repo <app repo>
```

Take the section ideas from the product's own pillars, as
`references/recipes.md` describes: the landing page's section titles, the
README's feature headings, or the core loop.

## 2. Decide the grid

- BPM from `DIRECTION.json` `music.bpm`. The loop length is a whole number of
  bars. At 120 BPM, 30 s is 15 bars: use 16 bars (64 beats, 32 s) and say
  "30 s" plainly. A half bar never resolves musically.
- Format from the venue (1920 x 1080 at 30 fps unless told otherwise).
- The loop length in frames is a whole number. The score uses that exact
  length (`references/loop.md`).

## 3. Storyboard as a hand-off table

Write `STORYBOARD.md` before any code. Each row has:
- the beats;
- the section's energy role (intro, build, drop, break, logo, outro);
- the product element on screen;
- the hand-off object into the next section;
- the sound.

Cut any row that shows no real product element, or that has no hand-off object.
Abstract motion with no product in it says nothing about the product. Run the
direction check again with `--storyboard STORYBOARD.md`.

## 4. Build

- Copy `assets/template/*` into `src/`, and `scripts/check_loop.py` and `scripts/finalize.sh` into `tools/`.
- Fill `theme.ts` and `fonts.ts` from `DIRECTION.json`. The magenta placeholders show in the first preview when you miss one.
- Write `src/timeline.json`. It holds bpm, fps, beats, the `music` block copied from `DIRECTION.json`, the sections with their `energy`, the handoffs, and the cues.
- Write one scene file per section. Each takes the section-local beat `b` and is a pure function of it. `Reel.tsx` picks the section by beat; there are no Remotion `Sequence` cuts.
- Time everything in beats: pops on beats, fast details on 8ths and 16ths.
- Exhibition rules: words at 120 px or more, one idea per bar, high contrast. Rows and log lines are texture only.
- The hero motion carries the hand-offs (`references/recipes.md`).

## 5. Score

```bash
cp <skill>/scripts/score.py <skill>/scripts/music.py audio/
uv run --with numpy --with scipy python audio/score.py
```

It reads `src/timeline.json`:
- the `music` block for the key, mode, progression, groove and effect timbre;
- the sections' `energy` roles for the arrangement;
- the cues (`{"beat", "sfx"}`).

It writes `public/score.wav` at -14 LUFS. Its bpm must equal the timeline's bpm.
The loop seam code is explained in `references/loop.md`.

## 6. Verify, then deliver

Render on the GPU when there is one. `--gl=angle` draws on the GPU, and
`--hardware-acceleration=if-possible` encodes on it when the codec allows, and
on the CPU otherwise:

```bash
npx tsc --noEmit -p .
npx remotion render Reel out/preview.mp4 --scale=0.5 --codec h264 --crf 23 --gl=angle
npx remotion render Reel out/render.mp4 --codec h264 --crf 18 --gl=angle --hardware-acceleration=if-possible
sh tools/finalize.sh out/render.mp4 public/score.wav out/<name>      # <name>.mp4 and <name>-x3.mp4
uv run --with numpy python tools/check_loop.py out/<name>.mp4         # hand-off and seam sheets
```

If `--gl=angle` fails, drop it. Read `checks/handoffs.png`: each boundary must
look like one object in motion. Read `checks/seam.png`: the last frames and
the first frames must be the same picture. Deliver the single loop and the 3x
file (for players that stutter on restart).

When the client accepts the reel, record its direction:

```bash
python3 <skill>/scripts/direction.py record DIRECTION.json --label "<product> reel <date>"
```

## References

| File | Read it when |
|---|---|
| `references/direction.md` | Writing DIRECTION.json: world, hero motion, palette, music |
| `references/recipes.md` | Writing a section: pillars, kinetic type, hand-offs, the mark |
| `references/loop.md` | Loop seam for picture and sound, and loudness |
| `references/arcs.md` | The arc and finale names DIRECTION.json allows |
| `references/brand.md` | A missing or new mark, palette tokens, fonts |
