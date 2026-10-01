# Recipes

Techniques, not a reel to copy. Every value is a function of the section-local
beat `b` (helpers in `assets/template/timeline.ts`). The look, the world and
the hero motion come from the film's `DIRECTION.json`.

## Sections from the product's own pillars

Take the section ideas from the product, never from an earlier reel:

1. The landing page's section titles and headline claims.
2. The README's feature headings.
3. The product's core loop, one stage per section.

Pick 3 to 6. Each section shows one real product element on screen (a screen,
a data shape, a result) and states one idea in one or two words.

## Kinetic type: a technique per idea

Match the motion to the meaning of the word. Invent; these are starting points.

| The idea is about | A motion that says it |
|---|---|
| speed, flow | the word arrives on streaks, skewed, and settles on the downbeat |
| change, flexibility | the letters bend on a wave; weight follows the wave |
| finding, precision | an outline word; a lens or a scan line shows the solid word inside |
| repetition, versions | echo copies stack, then collapse into one |
| structure, building | letters turn into blocks that link or stack |
| scale, many | the word tiles until it fills the frame, then one tile stays |
| privacy, safety | the word locks: a shape closes around it |
| connection | two words reach toward each other and join at one letter |

Rules:
- One idea per bar or per four beats. It must read in the first beat.
- Words at 120 px or more for a screen seen from a distance.
- Add one product element to every word, so the idea is about this product.
- Keep the direction of motion across a cut: when word A leaves downward, word
  B enters from above.

## Hand-offs

Every cut hands one object to the next section. `assets/template/Handoff.tsx`
shows the timing pattern with a plain shape. Build the reel's hand-offs from
its hero motion, so the transitions are as particular as the product:

| Pattern | The object |
|---|---|
| grow to fill | a shape from the outgoing section grows until it is the next background |
| dive | the camera zooms into one element; its fill becomes the next frame |
| collapse | everything shrinks into one dot or line; the next section grows from it |
| carry | an object moves across the cut and becomes the first element of the next section |
| wipe by motion | the hero motion (a scan line, a fold, a wave) passes over the frame and leaves the next section behind |

- Hold one colour until the shape is thin or the frame is full, then switch.
  A 50/50 mix of two brand colours often turns muddy.
- List every hand-off inside a section in `timeline.json` `handoffs`, so the
  check sheet covers it.

## Building on the beat

- Pop elements on the beat (`back.out`), draw lines with `pathLength=1` and a
  dash offset, and move small details on the 8ths and 16ths.
- Accelerating montages read as "and it does all this": 1, 1/2, 1/4, 1/8 beat
  per card. Early cards are read; late cards are energy.
- Start zoomed in so the first elements read from a distance, then pull back.
- A breath before the mark: one beat where the music drops out (`gate` in
  `timeline.json`) and one object holds still.

## The mark

- Drive each part of the mark by its own 0..1 value, and land its key part on
  the music's logo hit (the start of the section with `"energy": "logo"`).
- For a loop, return the mark to the opening state: the last frame is the
  first frame (`loop.md`).
