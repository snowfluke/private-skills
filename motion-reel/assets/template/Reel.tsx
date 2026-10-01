import { AbsoluteFill, Audio, staticFile, useCurrentFrame } from "remotion";
import { C } from "./theme";
import T from "./timeline.json";
import { SECTIONS, beatOf } from "./timeline";

// One scene component per section id in timeline.json. Each is a pure function of its
// section-local beat `b`. Fill this map with the film's own scenes.
const SCENES: Record<string, React.FC<{ b: number }>> = {};

// A small camera kick where a drop or the logo lands, from the sections' energy roles.
const KICKS = SECTIONS.filter((s: { energy?: string }) => s.energy === "drop" || s.energy === "logo").map((s) => s.start);

export const Reel: React.FC = () => {
  const frame = useCurrentFrame();
  const B = beatOf(frame);
  const s = SECTIONS.find((x) => B >= x.start && B < x.start + x.len) ?? SECTIONS[SECTIONS.length - 1];
  const Scene = SCENES[s.id];
  if (!Scene) throw new Error(`no scene component for section "${s.id}" in Reel.tsx`);
  const shake = KICKS.reduce((acc, at) => acc + (B >= at ? 10 * Math.exp(-(B - at) * 6) : 0), 0);
  return (
    <AbsoluteFill style={{ background: C.canvas }}>
      <AbsoluteFill style={{ transform: `translate(${Math.sin(frame * 2.3) * shake}px, ${Math.cos(frame * 3.1) * shake}px)` }}>
        <Scene b={B - s.start} />
      </AbsoluteFill>
      <Audio src={staticFile("score.wav")} />
    </AbsoluteFill>
  );
};

export const REEL_FRAMES = Math.round(T.beats * (60 / T.bpm) * T.fps);
