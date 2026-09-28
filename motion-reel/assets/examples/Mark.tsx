// The Beaverflow mark (assets/brand/mark.svg), with each part driven by a 0..1 progress.
export type MarkParts = { tile: number; ears: number; muzzle: number; eyes: number; nose: number; teeth: number; blink?: number };

const pop = (p: number) => Math.max(0, Math.min(1, p));

export const Mark: React.FC<{ size: number; parts: MarkParts; id: string }> = ({ size, parts, id }) => {
  const g = `url(#${id}-g)`;
  const s = (p: number, cx: number, cy: number) => `translate(${cx} ${cy}) scale(${pop(p)}) translate(${-cx} ${-cy})`;
  const eyeY = 1 - (parts.blink ?? 0) * 0.9;
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" style={{ overflow: "visible", display: "block" }}>
      <defs>
        <linearGradient id={`${id}-g`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#F7A93B" />
          <stop offset="1" stopColor="#DB5E17" />
        </linearGradient>
      </defs>
      <g transform={s(parts.ears, 31, 30)}><circle cx={31} cy={27} r={13} fill={g} /></g>
      <g transform={s(parts.ears, 89, 30)}><circle cx={89} cy={27} r={13} fill={g} /></g>
      <g transform={s(parts.tile, 60, 67)}><rect x={10} y={22} width={100} height={90} rx={30} fill={g} /></g>
      <g transform={s(parts.muzzle, 60, 82)}><ellipse cx={60} cy={82} rx={26} ry={19} fill="#FFE2BE" /></g>
      <g transform={`translate(0 55) scale(1 ${pop(parts.eyes) * eyeY}) translate(0 -55)`}>
        <circle cx={42} cy={55} r={6.5} fill="#1A1208" />
        <circle cx={78} cy={55} r={6.5} fill="#1A1208" />
      </g>
      <g transform={s(parts.nose, 60, 72)}><rect x={50} y={66} width={20} height={12} rx={6} fill="#1A1208" /></g>
      <g transform={`translate(0 ${(1 - pop(parts.teeth)) * -12}) translate(0 80) scale(1 ${pop(parts.teeth)}) translate(0 -80)`}>
        <rect x={52} y={80} width={7.5} height={16} rx={2.5} fill="#FFFFFF" />
        <rect x={60.5} y={80} width={7.5} height={16} rx={2.5} fill="#FFFFFF" />
      </g>
    </svg>
  );
};
