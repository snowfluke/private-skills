# Scene recipes

## Frame layout

```
x: 0      140            740  800                                  1860  1920
   +------+---------------+----+-------------------------------------+----+
   |      | CAPTION       |    | APP WINDOW (.app, white, r=20)      |    |  y 90
   |      | label         |    |                                     |    |
   |      | Title         |    |  real UI of the product             |    |
   |      | description   |    |                                     |    |
   |      | (from y 250)  |    |                                     |    |  y 990
   +------+---------------+----+-------------------------------------+----+
```

- The caption column is x 140 to 740, from y 250. Put nothing else on the left.
- All UI lives in the right region, x 800 to 1860, y 90 to 990 (max 1060 × 900).
  Scale a window down to fit. Do not crop it.
- Inside windows, body text is at least 16 px, table text at least 17 px, and
  headings are 24 to 34 px.
- Full-width scenes (the build editor, the finale) drop the caption and use the
  whole frame.

## Caption standard

Every explainer scene uses exactly one caption block. The styles are in
`assets/theme.css` (`.cap`, `.cap-label`, `.cap-title`, `.cap-desc`). The motion
is in `assets/caption.js` (`capIn`, `capOut`).

```html
<div class="cap" id="<id>-cap">
  <div class="cap-label">Step 03 · Matching</div>
  <div class="cap-title">Match automatically</div>
  <div class="cap-desc">Match records by key, or without one through layered rules with tolerance.</div>
</div>
```
```js
window.capIn(tl, "<id>-cap", 0.05);
window.capOut(tl, "<id>-cap", DUR - 0.35);
```

| Part | Rule | Bad | Good |
|---|---|---|---|
| label | `GROUP · NAME`. Groups: `Step 01`–`Step NN` for the core loop, then `Run`, `Review`, `Report`, or the product's own phase words. | `STEP 01 · INGESTION` then a title "Ingestion." | `Step 01 · Ingestion` |
| title | A 2 to 4 word action phrase. No period. Never repeats the label. | "Ingestion." | "Pull data from anywhere" |
| desc | One factual sentence of 25 words or fewer. Real capabilities only, taken from the code or the docs. | "Streamline your workflow." | "Fetch files from SFTP, email, APIs and storage." |

Write all captions into one copy table in `STORYBOARD.md` first. Review the
table as a set. Consistency is what the client checks.

## The explainer recipe: configure, then process

Each core-loop step gets one scene, 3.5 to 7 s long:

```
0.0  caption in, app window in
0.4  the REAL config UI for this step: dialog, form or panel with real labels.
     The cursor sets one or two values that matter.
~40% cut or morph to the process visualization:
     the input (files, records, requests) moves through the step
     and lands transformed in the output. Use real-looking data.
~85% a completion toast or result badge, held for reading time
DUR-0.35  caption out, window out
```

- Show the process with real objects. Fields fly from a raw file into typed
  columns. Pairs of rows lock together. Flags stamp onto rows. Do not use
  abstract blobs.
- A flying chip must carry visible text: a white pill, a colored border and dark
  mono text. An empty box reads as a bug.
- If the build scene already showed this step's config, do not show it again.
  Go straight to the process or to the outcomes.
- For an output step, show the fan-out: one result that goes to email, a webhook
  and storage.

## The build scene (the product's main screen)

This is one long scene on track 1. The explainers cut in over it on track 2.

- Build the screen from the app's real components: palette, canvas, inspector,
  logs panel. Use the real icon set.
- Build in segments, one per core-loop step. After each segment, leave a 3 to
  6 s gap. The explainer scene covers the gap. Then resume.
- Open the real config dialog for one representative item per segment. Put each
  panel to its real use (a logs panel shows logs).
- Move the camera Screen Studio-style: one eased zoom toward the work, then back
  out. See `motion.md`.
- If the product is collaborative, show a second named cursor with a presence
  avatar. Split the build between the two cursors.
- If an item produces a file, open its real editor and show one binding land.
- End with a test or preview run whose logs stream in the real panel.

## Pages never load

A recreated page must arrive with its body. Read the real page component and
rebuild what sits under the header (stats, cards, lists). Bring the content in
with the window, within 0.1 s. When the scene switches pages, fade the old one
out (0.15 s), then fade the new one in (0.25 s) with its content. A white window
with only a header reads as a loading state.

## Operate scenes

- Automation first. Show a schedule set in the real settings UI (for example a
  cron expression, three runs a day), then the monitor that lists the runs.
- Then on demand. Show a run dialog, then the run detail with per-step log
  lines that stream in, and a Gantt whose bars grow in step order. Never show a
  static spinner.

## Review and result

- Show real interactions: a bulk action on selected rows, a tab switch between
  sheets, an inline edit.
- A state change ("mark final", "approve", "publish") morphs into the result view
  inside the same scene. The changed item highlights. Do not cut to a new scene.
  Start the morph as soon as the state change settles (a 0.6 s morph). Hold the
  result about 0.8 s after its last reveal, then exit.
- Show realistic volume: a full month, not one day. Stream the rows in with a
  stagger and a scroll.

## Finale sequence (about 25 s)

```
node rain ──> card wall ──> "and many more..." ──> logo + pillar pills ──> credits over marquee
 ~7 s          ~2.5 s        no gap before it       ~3 s hold               10 s
```

1. **Node rain.** For each feature category: the category title appears in the
   center. Its items pop in place on one or two tight ellipses around the title.
   Each item wiggles in place (non-blocking, so the next pops meanwhile). Then
   they all fall off-screen. Each category is faster than the one before.
   Use the real icons.
2. **Card wall.** The product's primitives as cards (icon, name, the app's own
   one-line description) pop in a grid and exit together.
3. **"and many more..."** starts the moment the wall exits. Hold it about 1.5 s,
   then leave a breath of about 1 s before the lockup (the lockup is the payoff).
4. **Lockup.** The logo, the real slogan, then the pillar tags as pills.
5. **Credits.** They rise from the bottom and fade out, over 10 s. Show the
   company line, the company slogan and the contact. Behind them run
   full-screen marquee rows of contributor names, in alternating directions,
   low contrast. When the client gives teams, use one row per team: the team
   name in small accent capitals, then its members, and a person appears in
   every team they belong to. Without teams, deal the names with a seeded
   shuffle so each name is in exactly one row (`motion.md`).

## Logo intro

Design the intro for the mark's shape. A flat geometric mark can spin and
snap. A mascot moves like itself: it surfaces, lands, bobs. Carry a line or
shape from the previous scene into the intro, so the cut connects. For
example, the flood's cyan line became the waterline the mascot rises out of.
Use a transparent cutout of the mascot, cropped to its bounds. A mascot
source often has a solid background.

## Phone viewers

- A corner hint for the first ~4 s: a rotate-phone icon that turns to
  landscape and a speaker icon that pulses, "Rotate your phone · Sound on".
  Snapshot the opening scene first, and use the corner it leaves empty.
- Subtitles at the bottom centre, 38 px, in a dark translucent pill, on their
  own track above every scene.
- Zoom dialogs and small UI to fill the frame (see SKILL.md, Build).

## Reusing and retiming scenes

- To speed up a reused scene, wrap it in a speed wrapper. Record `speed`,
  `old_start` and `old_dur` in `timeline.json` so the score can remap its cues.
- To insert content in the middle of a long scene, shift every later segment
  with a time proxy (`motion.md`). Then push the later scenes back in
  `timeline.json`. Do not compress existing tweens.
