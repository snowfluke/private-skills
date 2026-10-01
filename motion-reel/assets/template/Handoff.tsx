import { AbsoluteFill } from "remotion";
import { lerp, out, ramp } from "./timeline";

// The mechanics of a hand-off, with no product content: one shape from the outgoing section
// grows until it is the incoming section's background. Replace the shape with the film's own
// hand-off object (its hero motion), keep the timing pattern: the object leads, the cut is hidden
// inside its motion, and the colour holds until the shape fills the frame.
export const GrowToFill: React.FC<{ b: number; from: number; to: number; x: number; y: number; size: number; color: string }> = ({
  b, from, to, x, y, size, color,
}) => {
  const p = ramp(b, from, to, out);
  const r = lerp(size / 2, Math.hypot(1920, 1080), p);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: x - r, top: y - r, width: 2 * r, height: 2 * r, borderRadius: "50%", background: color }} />
    </AbsoluteFill>
  );
};
