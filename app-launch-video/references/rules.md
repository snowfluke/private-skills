# Rules from earlier productions

Each rule came from a client correction. Apply the rule; the examples are not a
template for the next film.

## Story

- A launch film sells outcomes. A click-by-click walkthrough reads as training
  material. Every second shows motion or a result.
- Ask which step the client sees as the product's signature, and give it the
  most screen time. The code does not rank features; the client does.
- Show configuration in the real UI first, then visualize the process. A fake
  config panel misstates how the product works.
- Make a state change ("approve", "publish") a morph inside the scene, not a
  cut to a new scene. A morph shows cause and effect.
- Show realistic volume: a month of data, not one row.
- Show progress as real log lines or a timeline that fills, never a spinner.
- Keep side features out of the main story. They dilute it.

## Brand and copy

- Take the name, the mark, the slogan, the principles and the font from the
  repository. Never write a slogan of your own. When the client asks for a new
  one, offer three or four with one recommended.
- Keep real names exact. Spell out abbreviations in explanations, unless the
  real UI shows them short.
- Remove any customer name from a film meant for everyone.
- When a source asset does not match its name (a logo file named for a
  different animal than the product), say so. Do not fix it silently.

## Pace

- No idle hold over 0.8 s, except reading time: about 0.3 s per word from the
  moment the whole line is visible. Measure holds with `hold_probe.mjs`; do not
  judge them by eye.
- Reveal a crowd of items in one stagger. Hold a reveal only until it is fully
  visible.
- Before the final mark, leave a breath of about 1 s. The mark is the payoff.
- A human-paced cursor: about 0.35 s to reach, a 0.55 s eased glide, then the
  drop. A robot-fast cursor breaks the illusion.

## Sound

- Write every cue from the tween constants in the scene script. Never place a
  cue by ear, and never nudge it after a measurement.
- A swell (whoosh, riser) is loudest mid-envelope. Start it early so its peak
  lands on the cue.
- Voiceover lines are literal: they describe what is on screen at that moment.
  Anchor each line to its visual beat, not to the scene start.
- Never state a number the film does not show.

## Process

- The first cut is usually too slow. Expect revision rounds, and keep every
  variant: clients merge the best parts of two.
- "Clean up" means processes and scratch files. Never delete a finished
  variant or overwrite a delivered render.
- Snapshot every scene a parallel worker built. Workers have shipped empty
  boxes that passed their own checks.
- Answer a numbered revision list number by number, in order.
- Decide layout and motion yourself. Ask the client only for facts: names,
  slogans, which step matters most.
