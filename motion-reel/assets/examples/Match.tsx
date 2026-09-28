import { AbsoluteFill } from "remotion";
import { C, MONO, UI } from "../theme";
import { inn, lerp, out, ramp } from "../timeline";

// Beats 16-24 (local 0-8). Starts inside the Key Matcher card (white); ends with the match bar filling
// the frame in amber, which is the SPEED background.
const REFS = ["00401", "00402", "00417", "00431", "00423", "RK-7781203"];
const AMTS = ["150,000", "2,500,000", "75,000", "1,250,000", "990,000", "425,000"];
const PAIRS = 4;
const FLAGS = [{ text: "Cut Off Time H+1", bg: "#fef3c7", fg: "#b45309" }, { text: "NEED_MANUAL", bg: "#fee2e2", fg: "#dc2626" }];

const RowPill: React.FC<{ x: number; y: number; text: string; amt: string; matched: number; w?: number }> = ({ x, y, text, amt, matched, w = 560 }) => (
  <div style={{ position: "absolute", left: x, top: y, width: w, height: 74, borderRadius: 14, display: "flex", alignItems: "center", gap: 24, padding: "0 24px",
    background: matched > 0 ? `rgba(34,197,94,${0.12 + matched * 0.1})` : "#f5f5f4", border: `2px solid ${matched > 0 ? C.ok : "#e7e5e4"}`,
    fontFamily: MONO, fontSize: 28, color: C.text }}>
    <span>{text}</span>
    <span style={{ marginLeft: "auto" }}>{amt}</span>
  </div>
);

export const Match: React.FC<{ b: number }> = ({ b }) => {
  const enter = ramp(b, 0, 0.6, out);
  const summary = ramp(b, 5.4, 6.0, out);
  const fill = ramp(b, 1, 6.6, (t) => t) * 0.992 + ramp(b, 6.6, 7.0) * 0.008;
  const grow = ramp(b, 7.0, 8.0, inn);
  const pct = Math.min(99.2, fill * 100);
  return (
    <AbsoluteFill style={{ background: "#fff", overflow: "hidden", fontFamily: UI }}>
      <div style={{ position: "absolute", inset: 0, opacity: 1 - summary * 0.85, transform: `scale(${lerp(1.08, 1, enter) - summary * 0.06})` }}>
        <div style={{ position: "absolute", left: 140, top: 90, fontSize: 64, fontWeight: 800, color: C.text, letterSpacing: "-0.03em", opacity: enter }}>Key Matcher</div>
        <div style={{ position: "absolute", left: 140, top: 176, fontFamily: MONO, fontSize: 26, color: "#6b635c", opacity: enter }}>INTERNAL DATA ⇄ REKENING KORAN</div>
        {REFS.map((ref, i) => {
          const y = 270 + i * 96;
          const pairAt = 1 + i * 0.5;
          const lock = i < PAIRS ? ramp(b, pairAt, pairAt + 0.35, out) : 0;
          const drop = i >= PAIRS ? ramp(b, 3.2 + (i - PAIRS) * 0.5, 3.7 + (i - PAIRS) * 0.5, inn) : 0;
          const left = { x: lerp(140, 380, lock), y: y + drop * (820 - y + (i - PAIRS) * 0) };
          const right = { x: lerp(1220, 980, lock), y };
          const it = i < 5 ? `TRX-0522-${ref}` : "—";
          const rk = i < PAIRS ? `TRX-0522-${ref}` : i === 4 ? "—" : ref;
          return (
            <div key={i} style={{ opacity: enter }}>
              {i !== 5 && <RowPill x={left.x} y={i >= PAIRS ? lerp(y, 860, drop) : left.y} text={it} amt={AMTS[i]} matched={lock} />}
              {i !== 4 && <RowPill x={i >= PAIRS ? lerp(1220, 1220, drop) : right.x} y={i >= PAIRS ? lerp(y, 860, drop) : right.y} text={rk} amt={i === 5 ? AMTS[5] : AMTS[i]} matched={lock} />}
              {i < PAIRS && lock > 0.9 && (
                <svg width={56} height={56} viewBox="0 0 40 40" style={{ position: "absolute", left: 932, top: y + 9, transform: `scale(${ramp(b, pairAt + 0.3, pairAt + 0.5, out)})` }}>
                  <circle cx={20} cy={20} r={18} fill={C.ok} />
                  <path d="M12 20 L18 26 L28 14" fill="none" stroke="#fff" strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              )}
            </div>
          );
        })}
        {FLAGS.map((f, k) => {
          const s = ramp(b, 4.3 + k * 0.5, 4.55 + k * 0.5, (t) => 1 + 2.7 * (t - 1) ** 3 + 1.7 * (t - 1) ** 2);
          return (
            <div key={k} style={{ position: "absolute", left: k === 0 ? 140 : 1220, top: 776, padding: "10px 22px", borderRadius: 999, background: f.bg, color: f.fg,
              fontSize: 30, fontWeight: 700, border: `2px solid ${f.fg}`, transform: `scale(${Math.max(0, s)}) rotate(${(1 - Math.min(1, s)) * -8}deg)`, whiteSpace: "nowrap" }}>
              {f.text}
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 330, textAlign: "center", opacity: summary, transform: `scale(${lerp(0.8, 1, summary)})` }}>
        <div style={{ fontSize: 240, fontWeight: 800, letterSpacing: "-0.05em", color: C.text, lineHeight: 1 }}>{pct.toFixed(1)}%</div>
        <div style={{ fontSize: 64, fontWeight: 600, color: "#15803d", marginTop: 10 }}>matched</div>
      </div>
      <div style={{ position: "absolute", left: 140, top: 990, height: 22, width: 1640, borderRadius: 11, background: "#f0eeec", opacity: 1 - grow }} />
      {/* The match bar: fills, then grows into the SPEED background. */}
      <div style={{ position: "absolute", left: lerp(140, 0, grow), top: lerp(990, 0, grow), height: lerp(22, 1080, grow), width: lerp(1640 * fill, 1920, grow),
        borderRadius: lerp(11, 0, grow), background: C.amber }} />
    </AbsoluteFill>
  );
};
