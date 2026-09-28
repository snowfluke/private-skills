# Lessons

This skill came from the Beaverflow exhibition reel (2026-09-26, UTC+7). It was built after a Remotion
reel for the same product, whose first half the client rejected.

| Time | Client request (shortened) | Rule | Why |
|---|---|---|---|
| 09-26 15:03 | "A 30-s motion graphics reel of Beaverflow, looped in an exhibition. The reference reel's first half was random motion graphics that don't represent the platform. I like the pillar motion from 17 s: speed, flexibility, inspection, iteration, visual abstraction. Act as an expert motion designer. Motion and graphics must represent the platform. Transitions interconnected. 140 BPM, make the music. No voiceover or subtitles. Make a skill when done." | Every section shows a real product feature (data flood, workflow nodes, matching, flags, Final Outputs, the mark). Every cut is a hand-off object. Keep the pillar kinetic type, and add a product element to each word. Loop picture and sound. | Abstract motion is pleasing but says nothing about the product. A reel on a booth screen is joined mid-loop, often muted, from a distance. |
| 09-26 15:03 | Earlier reel work for the same product (launch film rounds). | Take the logo, palette and font from the brand work (`app-launch-video/references/brand.md`). A rebrand that changes the mark changes the logo build and the loop line. | The reel and the launch film must look like one brand. |
| 09-26 16:00 | "Change the 'Every day. Final' part after Visual Abstraction; it doesn't fit. Add an incremental-speed montage of all our features, then collapse into a dot, then the logo reveal." | Before the logo, show the whole product in an accelerating montage (1, 1/2, 1/4, 1/8 beat per card). End on one object that the logo can grow from: a dot. Give the dot a breath of silence. | A single-feature scene before the logo felt like an extra step. A montage of everything reads as "and it does all this", and the dot gives the logo a clean start. |

Build notes that cost time:
- 70 beats at 140 BPM is exactly 30 s, but that is 17.5 bars; the loop would never resolve. Use 72 beats.
- 72 beats is 925.7 frames. A 926-frame video and a 925.7-frame score drift 10 ms per loop. Size the score to the frames.
- Remotion's AAC track came out 45 ms longer than the picture, and concatenating finished AAC tracks drifted 21 ms. Mux from the WAV, cut to the video length.
- A single-pass loudness filter ramps its gain. Use two passes with `linear=true`.
- A colour mix of orange and teal at 50% is olive. Hold one colour until the shape is thin, then switch.
- Section starts are not the only hand-offs. List the pillar changes inside a section as `handoffs` in `timeline.json`, so the check sheet covers them.
