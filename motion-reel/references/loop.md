# The loop seam

A viewer never sees the start. So the seam must be invisible in picture and in
sound.

## Picture

- The last frame and frame 0 are the same picture. Design the ending to arrive
  at the opening state, and hold it for about 0.5 beat, so the seam reads as a
  breath.
- Keep the direction of motion across the seam. The logo stretches out into a
  line, and the line then opens outward.
- The total frame count is `round(beats × fps × 60 / bpm)`. At 72 beats, 140
  BPM and 30 fps, that is 926 frames. The last frame is beat 71.94.
- Check the seam: play the file twice and tile the frames around the wrap
  (`check_loop.py`, `seam.png`).

## Sound

- Loop length = the video length exactly: `LEN = round(beats × 60 / bpm × fps) / fps`,
  and `BEAT = LEN / beats`. The tempo stretches by under 0.04%, which is
  inaudible. Otherwise the audio drifts about 10 ms per loop from the picture.
- Render with a tail (two bars) past the loop end, then add the tail onto the
  start. Reverb, ringing chords and the riser's end then continue across the
  seam. Sum the tail; do not cut it.
- Use no fade-in and no fade-out.
- End on a riser and a snare roll that resolve onto beat 0's downbeat hit. The
  first 50 ms are then louder than the last 50 ms on purpose: that is the hit,
  not a click.
- Loudness: two-pass `loudnorm` with `linear=true` (one static gain). A
  single-pass `loudnorm` changes gain over time and can leave a step at the
  seam. Target about -14 LUFS for a venue loop.

## Delivery

- Mux the picture with the WAV, cut to the video's exact duration
  (`finalize.sh`). Remotion's own AAC track ran 45 ms longer than the picture.
- Make a 3× file too. Concatenate the video, and loop the WAV three times for
  its audio. Concatenating finished AAC tracks drifted 21 ms from encoder
  padding.
