import { AbsoluteFill, Audio, staticFile, useCurrentFrame } from "remotion";
import { Build } from "./scenes/Build";
import { Flood } from "./scenes/Flood";
import { Logo } from "./scenes/Logo";
import { Match } from "./scenes/Match";
import { Montage } from "./scenes/Montage";
import { Pillars } from "./scenes/Pillars";
import { C } from "./theme";
import { SECTIONS, beatOf } from "./timeline";

const SCENES: Record<string, React.FC<{ b: number }>> = { flood: Flood, build: Build, match: Match, pillars: Pillars, montage: Montage, logo: Logo };
// Small camera kicks on the downbeats that land a new idea.
const KICKS = [{ at: 8, amp: 8 }, { at: 24, amp: 12 }, { at: 44, amp: 8 }, { at: 58, amp: 14 }];

export const Reel: React.FC = () => {
  const frame = useCurrentFrame();
  const B = beatOf(frame);
  const s = SECTIONS.find((x) => B >= x.start && B < x.start + x.len) ?? SECTIONS[SECTIONS.length - 1];
  const Scene = SCENES[s.id];
  const shake = KICKS.reduce((acc, k) => acc + (B >= k.at ? k.amp * Math.exp(-(B - k.at) * 6) : 0), 0);
  return (
    <AbsoluteFill style={{ background: C.ink }}>
      <AbsoluteFill style={{ transform: `translate(${Math.sin(frame * 2.3) * shake}px, ${Math.cos(frame * 3.1) * shake}px)` }}>
        <Scene b={B - s.start} />
      </AbsoluteFill>
      <Audio src={staticFile("score.wav")} />
    </AbsoluteFill>
  );
};
