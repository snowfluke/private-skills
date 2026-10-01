# Direction: one film, one product

Every film gets its own `DIRECTION.json` before any storyboard. It holds every
creative choice and the reason for it. The skill has no default look, no
default story and no default music: a choice you do not make in this file does
not exist. `scripts/direction.py check` rejects a direction that is untraced or
too close to an earlier film.

## Where the facts come from

| Read | For |
|---|---|
| `README.md`, the docs index, the docs' first pages | What it does, for whom, the words the team uses for it |
| The landing page (the `homepage` field in `package.json`, the repo's website link, or a URL in the README). Fetch it with `ax` when it is installed, otherwise `curl`. | The tone words, the headline, the section titles: these are the product's own pillars |
| The main screen and its components | The mechanic: what the product physically does to its input |
| Theme tokens, logo files, the font the UI renders | The brand colours, the mark, the type |

Quote what you find. A field with `evidence` names a file in the app repo
(`path` or `path#L12`) or a URL.

## The fields

```json
{
  "product":  {"name": "...", "evidence": "README.md#L1"},
  "mechanic": {"verb": "scan", "what": "reads text out of receipt photos", "evidence": "README.md#L5"},
  "audience": {"value": "...", "evidence": "..."},
  "tone":     {"words": ["private", "instant"], "evidence": "https://... (quote the words)"},
  "metaphor": {"value": "...", "why": "..."},
  "arc":      {"value": "journey", "why": "..."},
  "hero_motion": {"family": "scan-reveal", "value": "...", "why": "..."},
  "finale":   {"value": "zoom-out-reveal", "why": "..."},
  "layout":   {"value": "lower-third", "why": "..."},
  "palette":  {"brand": ["#..."], "invented": ["#...", "#...", "#..."], "canvas": "#...", "evidence": "src/theme.css#L3"},
  "music":    {"bpm": 88, "root": "Eb", "mode": "dorian", "progression": ["i", "IV", "VII", "i"],
               "preset": "minimal-tick", "swing": 0.1, "timbre": "analog", "why": "..."}
}
```

Copy `music` into `timeline.json` unchanged. The score reads it from there.

### mechanic: the physical verb

Name what the product does to things, as a verb a child could act out:
scan, match, sort, route, grow, stack, translate, listen, compress, stitch,
watch, sign. Every motion choice below follows from this one word. A launch film
that shows the verb happening is about the product. One that shows generic
dashboards is about any product.

### metaphor and theme

Invent a world the verb lives in, then design the film inside it. The brand
stays real; the world around it is new.

| Verb | Possible worlds (invent your own) |
|---|---|
| scan, read | a darkroom where text develops; a lighthouse beam; an archive under a lamp |
| match, reconcile | a loom where threads cross; a zipper closing; magnets snapping to pairs |
| route, orchestrate | a rail yard with switching points; a pneumatic-tube office; a river delta |
| grow, generate | a greenhouse; a printing press; crystals forming |
| listen, speak | a waveform landscape; a radio tower; a choir of dots |
| compress, pack | a suitcase packed by a robot; origami folding; a hydraulic press |

The world sets the canvas, the texture (paper grain, film grain, blueprint
lines, glass), the shapes, and how things enter and leave.

### arc and finale

Pick one arc from `arcs.md` for the product's shape, and say why in one line.
Pick the finale from that arc's list.

### hero_motion: the signature move

One motion device that is the verb made visible. It carries the transitions of
the whole film. Name its `family` in a short kebab-case term and describe it.

| Verb | Hero motion examples |
|---|---|
| scan | a light bar sweeps and leaves the next scene behind it |
| match | two halves slide together and lock with a snap, and the seam becomes the next frame's edge |
| route | a packet travels a line, and the line bends to become the next layout |
| grow | a seed point branches into the next screen's structure |
| listen | a waveform flattens into a horizon line that the next scene stands on |
| compress | the frame folds in half twice and unfolds into the next scene |

The motion recipes in `motion.md` are infrastructure: camera, cursor, seek
safety. Copy them. The hero motion is invented per film.

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

`brand` holds the product's real colours from the repo. `invented` holds at
least three colours of the film's world, chosen to sit with the brand: a canvas,
a light, and an accent. Pick them from the metaphor (darkroom: amber safelight
on near-black; greenhouse: leaf green on chalk). Keep text contrast at 4.5:1 or
more. Write the canvas as `canvas`.

### music

| Tone words | Tempo | Mode | Preset |
|---|---|---|---|
| calm, careful, private, precise | 70 to 95 | dorian, minor, lydian | `minimal-tick`, `ambient-drift` |
| friendly, simple, open | 95 to 115 | major, mixolydian | `broken-beat`, `motorik` |
| fast, bold, powerful, automated | 118 to 135 | minor, phrygian, mixolydian | `pulse-house`, `half-time` |
| playful, creative | 100 to 125 | lydian, major | `broken-beat`, `pulse-house` |
| technical, relentless, scale | 120 to 140 | minor, dorian | `motorik`, `half-time` |

- Write the progression as 2 to 8 roman numerals. The mode sets each chord's quality.
- Set `swing` from 0 to 0.35 for a human feel.
- Pick the `timbre` for the sound effects from the world:
  - glass for light and optics
  - wood for paper and craft
  - analog for warmth
  - digital for code
  - soft for calm
  - metal for machines
- `music.py` lists every allowed value.

## Check, then record

```bash
python3 <this skill's dir>/scripts/direction.py check DIRECTION.json --repo <app repo> --storyboard STORYBOARD.md
```

Fix every error. A direction too close to an earlier film names the shared
choices: change all but two. After delivery, record the film so the next one
differs from it:

```bash
python3 <this skill's dir>/scripts/direction.py record DIRECTION.json --label "<product> <date>"
```
