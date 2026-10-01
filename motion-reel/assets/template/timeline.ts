import { Easing, interpolate } from "remotion";
import T from "./timeline.json";

export type Section = { id: string; start: number; len: number; energy?: string };

export const FPS = T.fps;
export const BPM = T.bpm;
export const FRAMES_PER_BEAT = (60 / BPM) * FPS;
export const TOTAL_FRAMES = Math.round(T.beats * FRAMES_PER_BEAT);
export const SECTIONS: Section[] = T.sections;

export const frameOf = (beat: number) => Math.round(beat * FRAMES_PER_BEAT);
export const beatOf = (frame: number) => frame / FRAMES_PER_BEAT;

export const sectionFrames = (s: Section) => {
  const from = frameOf(s.start);
  return { from, durationInFrames: frameOf(s.start + s.len) - from };
};

export const snap = Easing.bezier(0.83, 0, 0.17, 1);
export const out = Easing.bezier(0.16, 1, 0.3, 1);
export const inn = Easing.bezier(0.7, 0, 0.84, 0);

// Progress 0..1 between two beats, clamped. `b` is the scene-local beat.
export const ramp = (b: number, from: number, to: number, easing: (t: number) => number = snap) =>
  interpolate(b, [from, to], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing });

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// 1 on the beat, decaying to 0 before the next one.
export const pulse = (b: number, decay = 6) => Math.exp(-(b - Math.floor(b)) * decay);

// Cubic bezier point for edges drawn left to right with horizontal tangents.
export const bez = (x0: number, y0: number, x1: number, y1: number, t: number) => {
  const mx = (x0 + x1) / 2, u = 1 - t;
  return { x: u ** 3 * x0 + 3 * u ** 2 * t * mx + 3 * u * t ** 2 * mx + t ** 3 * x1, y: u ** 3 * y0 + 3 * u ** 2 * t * y0 + 3 * u * t ** 2 * y1 + t ** 3 * y1 };
};

// Deterministic 0..1 from an integer.
export const hash = (n: number) => (((Math.sin(n * 127.1 + 311.7) * 43758.5453) % 1) + 1) % 1;
