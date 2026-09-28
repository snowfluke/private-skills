---
name: motion-reel
description: Build a short, looping, music-driven motion-graphics reel (15 to 45 s) that shows a product through motion, with no voiceover and no subtitles. It is made for an exhibition screen, a booth, a lobby display, a showreel, or a social loop. It uses Remotion with a beat-grid timeline, hand-off transitions between every section, a seamless picture-and-sound loop, and an offline-synthesized score at a set BPM. Use it for requests like "30-second reel for the exhibition", "looping motion graphics for our booth", "a 140 BPM brand reel", "make it loop seamlessly", "motion graphics that explain our pillars", or revisions to a reel made this way. Use `app-launch-video` for a narrated launch film of an app, and `brag-slim` for a one-off 20 s share clip.
compatibility: Needs Node with npx, Remotion (a Remotion project, or copy the template), ffmpeg, and Python 3 with numpy and scipy (uv works).
---

<!-- Private repo: the absolute ~/.claude/skills/ paths below are intentional. This skill and its sibling media skill are installed only on the maintainer's machine. -->

# Motion reel

A loop that a passer-by can join at any second. Every section shows a real part
of the product. Every cut hands one object to the next section. The last frame
is the first frame, and the music wraps with it.

## 0. Prerequisites

| Need | Check | Fix |
|---|---|---|
| Node, npx | `node -v` | Node 20 or later |
| Remotion project | `npx remotion versions` in the project | Copy an existing reel project (with `node_modules`), or `npx create-video@latest` and copy `assets/template/*` into `src/` |
| ffmpeg | `ffmpeg -version` | `brew install ffmpeg` |
| numpy, scipy | `uv --version` | `uv run --with numpy --with scipy python …` |

For brand work (mark, palette, font), read `~/.claude/skills/app-launch-video/references/brand.md`.

## 1. Decide the grid first

- BPM from the brief (default 140). Loop length = a whole number of bars.
  At 140 BPM, 30 s is 17.5 bars, so use 18 bars (72 beats, 30.86 s) and say
  "30 s" plainly. A half-bar loop never resolves musically.
- Format from the reference or the venue (1920 × 1080 at 30 fps by default).
- The loop length in frames is a whole number (926 frames). The score uses that
  exact length, so its tempo stretches by under 0.04%. See `references/loop.md`.

## 2. Storyboard as a hand-off table

Write `STORYBOARD.md` before any code. Each row has the beats, the platform
feature on screen, the hand-off object, and the sound. Cut any row that shows
no real product feature or has no hand-off object. The client rejected a
reference reel because its first half was "random motion graphics that don't
represent the platform". Example: `assets/examples/STORYBOARD.md`.

Hand-off objects that worked (details in `references/recipes.md`):

| From → to | Object |
|---|---|
| Loop end → opening | a thin line across the middle |
| Data flood → workflow | the streams pull into two glowing orbs, and nodes pop where they land |
| Workflow → a node's inside | the camera dives into one node; its white card becomes the next frame |
| Progress → next colour | the progress bar fills, then grows to fill the frame |
| Streak → colour | the last speed streak widens to cover the frame |
| Click → colour | the click ring grows to fill the frame |
| Lens → colour | the magnifier lens grows until its inside is the whole frame |
| Word → word | one word falls out of frame while the next falls in from above: same direction |
| Letters → nodes | letters become boxes linked by edges |
| Box → montage | the camera dives into a box; its fill becomes the first card |
| Montage → logo | the last card collapses into a dot; the logo grows from it |
| Logo → loop line | the face goes, and the tile stretches into the opening line |

## 3. Build

- One scene file per section. Each takes the section-local beat `b` and is a
  pure function of it. The Reel picks the section by beat; there are no
  Remotion `Sequence` cuts and no white flashes to hide a cut.
- Time everything in beats: `ramp(b, from, to, easing)`, pops on beats, fast
  details on 8ths and 16ths. The timeline helpers are in `assets/template/timeline.ts`.
- Exhibition rules: words ≥ 120 px, one idea per bar, high contrast. Rows,
  logs and node sub-labels are texture only. No timecode HUD.
- Vendor the fonts and wait for them (`assets/template/fonts.ts`). A variable
  font without a `wdth` axis needs `scaleX` for squash effects.
- Kinetic type per idea (Speed, Flexibility, Inspection, Iteration, Visual
  Abstraction): `references/recipes.md` and `assets/examples/Pillars.tsx`. Add
  one product element to each word (a Gantt racing, a dragged edge, a log line
  under the lens, version tags, letters becoming nodes).

## 4. Score

Copy `scripts/score.py` to `audio/score.py`. It reads `src/timeline.json` for
the tempo, length and cue list (`{"beat", "sfx"}`), and writes
`public/score.wav` at -14 LUFS. Rewrite only its arrangement block: an intro,
the groove, a drop where the main idea lands, a breakdown, then the logo hit
and a riser that resolves onto beat 0. The loop-safe parts (tail fold,
two-pass linear loudness, frame-exact length) are explained in
`references/loop.md`.

## 5. Verify, then deliver

```bash
npx tsc --noEmit -p .
npx remotion render Reel out/preview.mp4 --scale=0.5 --codec h264 --crf 23    # ~20 s
npx remotion render Reel out/render.mp4 --codec h264 --crf 18
sh tools/finalize.sh out/render.mp4 public/score.wav out/<name>                # <name>.mp4 and <name>-x3.mp4
uv run --with numpy python tools/check_loop.py out/<name>.mp4                  # hand-off and seam sheets
```

Read `checks/handoffs.png`: each boundary must look like one object in motion.
Read `checks/seam.png`: the last frames and the first frames must be the same
picture. Deliver the single loop and the 3× file (for players that stutter on
restart).

## References

| File | Read it when |
|---|---|
| `references/recipes.md` | Writing a section: pillar type, hand-offs, node graph, calendar, logo build |
| `references/loop.md` | Loop seam for picture and sound, and loudness |
| `references/lessons.md` | Before planning: what the client asked for and why |
| `assets/examples/` | A complete 72-beat reel (Beaverflow) to copy from |
