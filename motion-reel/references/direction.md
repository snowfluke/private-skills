# Direction: one film, one product

Every film gets its own `DIRECTION.json` before any storyboard. It holds every
creative choice, the reason for it, and the options it beat. The skill has no
default look, story or music: a choice you do not make in this file does not
exist. `scripts/direction.py check` rejects a direction that is untraced, padded,
or too close to an earlier film.

## Where the facts come from

Look in this order, and write in `PRODUCT.md` what each step found:

1. The landing page. Find it in `package.json` `homepage` (unless it points
   back to the repo), the README's links, or the repo's website field.
2. The package page (npm, JSR, PyPI, crates.io), the docs site, or a live
   demo or playground.
3. The README and the docs index. When nothing above exists, the README is
   the tone source. Say so in `PRODUCT.md`.

Fetch pages with `ax` when it is installed, otherwise `curl`. When sources
disagree, the code wins, then the newest document.

| Read | For |
|---|---|
| The pages above | The tone words, the headline, the section titles: the product's own pillars |
| The main screen, or for a library the API a user calls | The mechanic: what the product physically does to its input |
| Theme tokens, logo files, the font the UI renders | The brand colours, the mark, the type |

A field with `evidence` names a file in the app repo (`path`, or `path#L12`
inside the file) or a URL. The check reads the cited file: tone words and
brand colours must appear in it. A URL source needs a `quote` copied from the
page that holds the tone words.

## Products without a screen

A library, an SDK, a CLI or an API has no UI to recreate. Its real screens
are:
- the code a user writes, in an editor;
- the terminal session;
- the artefact it produces: an image with boxes drawn on it, a file, a response;
- its demo or playground, when it has one.

Film those. With no logo, set the name as a wordmark in the film's display
face. Design a mark only when the client asks (`brand.md`).

## The fields

```json
{
  "format":   "film | loop",
  "product":  {"name": "<name>", "evidence": "<file#Ln or URL>"},
  "mechanic": {"verb": "<one verb>", "what": "<what it does to its input>", "evidence": "<...>"},
  "audience": {"value": "<who>", "evidence": "<...>"},
  "tone":     {"words": ["<word>", "<word>"], "evidence": "<...>", "quote": "<only for a URL>"},
  "metaphor": {"value": "<the film's world>", "why": "<...>"},
  "arc":      {"value": "<from arcs.md>", "why": "<...>", "rejected": ["<arc: reason>", "<arc: reason>"]},
  "hero_motion": {"family": "<kebab-case>", "value": "<the motion>", "why": "<...>", "rejected": ["...", "..."]},
  "finale":   {"value": "<from arcs.md>", "why": "<...>"},
  "layout":   {"value": "<see below>", "why": "<...>"},
  "palette":  {"brand": ["#..."], "invented": ["#...", "#...", "#..."], "canvas": "#...", "ink": "#...", "evidence": "<...>"},
  "music":    {"bpm": 0, "root": "", "mode": "", "progression": [], "preset": "", "swing": 0, "timbre": "",
               "why": "<...>", "rejected": ["...", "..."]}
}
```

- Every `why` uses at least six different words and names the mechanic, a tone
  word or the world it serves.
- `rejected` lists two options you considered, each with its reason. Write it
  before you settle: the first idea that comes to mind is usually the one every
  film gets.
- Copy `music` into `timeline.json` unchanged. The score reads it from there.

### mechanic

Name what the product does to things, as one verb a child could act out. Every
motion choice follows from it. A film that shows the verb happening is about
the product. One that shows generic dashboards is about any product.

### metaphor: the film's world

Invent the world the verb lives in. The brand stays real; the world is new.

1. List the nouns the product's own docs use: its inputs, outputs, users, places.
2. For each, write one physical place or craft where that thing is handled by
   hand: a workshop, a trade, a machine, a natural process.
3. Write five candidate worlds. Cross out the first two that came to mind and
   any world in your history. Pick the one whose motion shows the verb most
   plainly.

The world sets the canvas, the texture (paper grain, film grain, chalk,
glass), the shapes, and how things enter and leave. Example, from a product no
film here was made for: a scheduling tool for beekeepers. Its nouns are hives,
inspections and seasons. The world is a honeycomb frame lifted from a hive.
Each scheduled inspection fills one cell with wax.

### arc and finale

Pick one arc from `arcs.md` for the product's shape. Pick the finale from that
arc's row. A loop (`"format": "loop"`) always ends on `loop-to-start`.

### hero_motion: the signature move

One motion device that is the verb made visible inside the world. It carries
every transition. Find it by acting the verb out with the world's objects. In
the beekeeping world, an inspection "fills": wax flows into a cell, and the
filled cell's shape becomes the next frame. Name its `family` in a short
kebab-case term.

Your skill's motion recipes (`motion.md` in app-launch-video, the helpers in
`timeline.ts` in motion-reel) are infrastructure: timing, camera, seek safety.
The hero motion is invented per film.

### layout

| Value | Fits when |
|---|---|
| `split-caption` | dense UI that needs a fixed explanation beside it |
| `lower-third` | wide UI or media that needs the full width |
| `full-bleed-type` | ideas over UI: type is the picture |
| `corner-index` | many short steps: a small step index in a corner, the UI fills the rest |
| `center-stack` | one object at a time, centred, caption under it |
| `no-caption` | a music film where the voiceover or the motion says it all |

### palette

`brand` holds the product's real colours, found in the cited file. `invented`
holds at least three colours of the film's world, chosen from its materials.
`canvas` is the background. `ink` is the text colour on it, at 4.5:1 contrast
or more; the check measures it. A brand colour that fails on the canvas is
an accent for shapes, never for text.

### music

Choose each axis on its own from the tone and the world. Do not take a row of
choices as a set.

| Axis | Choose from | Guide |
|---|---|---|
| Tempo | 60 to 160 BPM | the energy of the tone: slower for calm or careful, faster for automated or bold. For a loop, pick a tempo that fills the length in whole bars (`seconds x bpm / 240` is whole). |
| Mode | major, minor, dorian, mixolydian, lydian, phrygian | the mood: lydian floats, dorian is cool and steady, mixolydian is open, phrygian is tense |
| Progression | 2 to 8 roman numerals | the motion: two chords for a steady machine, four or more for a journey |
| Preset | pulse-house, broken-beat, half-time, motorik, minimal-tick, ambient-drift | the world's rhythm: a production line, a heartbeat, footsteps, wind |
| Swing | 0 to 0.35 | 0 for machines, 0.1 to 0.2 for people |
| Timbre | glass, wood, analog, digital, soft, metal | the world's materials: what its objects would sound like when they touch |

`music.py` lists every allowed value. The check counts tempo, key, preset and
timbre against your history.

## Check, then record

```bash
python3 <skill>/scripts/direction.py check DIRECTION.json --repo <app repo> --storyboard STORYBOARD.md
```

Fix every error. A direction too close to an earlier film names the shared
choices: change all but two. After delivery, record the film so the next one
differs from it:

```bash
python3 <skill>/scripts/direction.py record DIRECTION.json --label "<product> <date>"
```

Directions you try but never deliver are not recorded. When you make several
films in one session, record each accepted one before you start the next.
