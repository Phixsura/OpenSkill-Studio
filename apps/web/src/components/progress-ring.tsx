"use client";

interface ProgressRingProps { percentage: number; circumference: number; offset: number;
  color: string; label: string; value: number; maxValue: number; size?: number; }

const ringColors: Record<string, string> = {
  green: "stroke-green-500", blue: "stroke-blue-500",
  yellow: "stroke-yellow-500", red: "stroke-red-500",
};

export function ProgressRing({ percentage, circumference, offset, color, label,
  value, maxValue, size = 120 }: ProgressRingProps) {
  const r = 45;
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox="0 0 100 100" className="-rotate-90">
          <circle cx="50" cy="50" r={r} fill="none" strokeWidth="8"
            className="stroke-gray-200 dark:stroke-gray-700" />
          <circle cx="50" cy="50" r={r} fill="none" strokeWidth="8"
            strokeLinecap="round" className={ringColors[color] ?? ringColors.blue}
            strokeDasharray={circumference} strokeDashoffset={offset} />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xl font-black">{percentage}%</span>
        </div>
      </div>
      {label && <p className="text-xs text-gray-400">{label}</p>}
      <p className="text-[10px] text-gray-300">{value} / {maxValue}</p>
    </div>
  );
}
