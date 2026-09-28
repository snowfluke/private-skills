# Recipes

All code is in `assets/examples/`. Every value is a function of the section-local beat `b`.

## Kinetic type for ideas (`Pillars.tsx`)

| Idea | Motion | Product element | Hand-off out |
|---|---|---|---|
| Speed | the word arrives from the left, skewed and blurred, on horizontal streaks; it settles on the downbeat | Gantt bars race; a timer counts to "1m 24s" | the last streak widens, skewed, until it covers the frame |
| Flexibility | letters bounce on a sine wave; weight and scale follow the wave | a cursor drags the middle of an edge between two nodes up and down on the beat | the cursor clicks; the click ring grows into the next colour |
| Inspection | a thin outline word; a lens sweeps across and shows the bold word inside | a real log line sits inside the lens | the lens stops and grows until its inside is the whole frame |
| Iteration | 8 echo copies stack upward (outlines), and the last one is solid | version tags v1-v8; a rerun arrow turns | the echoes collapse; the solid word falls out of frame downward |
| Visual abstraction | letters fly in, turn into boxes, and edges link them | the boxes are nodes | the boxes re-flow into the next layout (a calendar grid) |

Rules:
- One word per four beats. It must be readable in the first beat.
- The background colour changes with each idea, and the hand-off carries the
  new colour in.
- Keep the direction of motion across a cut. When word A falls out downward,
  word B falls in from above.

## Workflow graph (`Build.tsx`)

- World-space node cards: an icon tile in the node group's tint, the name, and
  a mono sub-label. The camera is `scale(z) translate(-cx, -cy)` around the
  frame centre.
- Pop nodes on the beat (`back.out`), and draw edges with `pathLength=1` and a
  dash offset. Send one packet per beat along each drawn edge.
- Start zoomed in (1.25) so the first nodes read from a distance, then pan and
  fit.
- Dive: from 2 beats before the cut, zoom about 14× into one node with an
  `inn` ease. At the cut, the card's white fills the frame and becomes the next
  section's background.

## Matching and flags (`Match.tsx`)

- Pairs lock on the 8ths: the two rows slide to the middle, turn green, and a
  check pops.
- Exceptions drop to a tray, and a flag chip slams onto each (`back.out` with
  a small rotation).
- A big counter takes over, then the progress bar fills and grows into the
  next background.

## Feature montage into a dot (`Montage.tsx`)

- One full-frame card per feature: an icon from the app's own icon set, the
  name at 150 px, and a small "07 / 26" counter. The background cycles through
  the palette, and the text switches dark or light with it.
- Speed the cuts up on the grid: 4 × 1 beat, 6 × ½, 8 × ¼, 8 × ⅛. Early cards
  are read; late cards are energy. Each card punches in (1.1 to 1).
- Hand-off in: dive the camera into one box of the previous section. The
  box's fill colour is the first card's background.
- Hand-off out: the last card's rectangle shrinks to a 30 px dot at the logo
  tile's centre and turns orange. Hold the dot for about 1 beat with one
  pulse. The music drops out for that breath (a gate on drums and synth; the
  effects stay).
- The logo tile then grows from the dot (scale from dot size to 1, `back.out`).

A calendar "Every day. Final." section was cut here. It showed one feature
where the client wanted all of them, and it did not lead into the logo.

## Logo build and the loop line (`Logo.tsx`, `Mark.tsx`)

- Drive each part of the mark by its own 0..1 value: tile, ears, muzzle, eyes,
  nose, teeth. The teeth land on the music's logo hit, with a 7% scale kick.
- Lockup: the mark slides and shrinks to the left, and the wordmark letters
  rise. The tagline arrives in two beats.
- Loop: the mark returns to the centre, the face scales out, and a div with
  the tile's geometry stretches into the opening line (width, height, radius).
  It stays orange until thin, then turns to the line colour. A 50/50 mix of
  orange and teal turned olive.
