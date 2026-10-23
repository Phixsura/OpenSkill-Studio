"use client";

interface SparklineChartProps { points: number[]; label: string; current: number;
  trend: "up" | "down" | "flat"; width?: number; height?: number; }

export function SparklineChart({ points, label, current, trend, width = 120, height = 32 }: SparklineChartProps) {
  if (points.length < 2) return <span className="text-xs text-gray-400">—</span>;

  const stepX = width / (points.length - 1);
  const path = points.map((y, i) => `${i === 0 ? "M" : "L"}${(i * stepX).toFixed(1)},${(height - (y / 100) * height).toFixed(1)}`).join(" ");
  const color = trend === "up" ? "#10B981" : trend === "down" ? "#EF4444" : "#6B7280";

  return (
    <div className="flex items-center gap-2">
      <svg width={width} height={height} className="overflow-visible">
        <path d={path} fill="none" stroke={color} strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <div className="text-right">
        <p className="text-sm font-bold" style={{ color }}>{current}</p>
        {label && <p className="text-xs text-gray-400">{label}</p>}
      </div>
    </div>
  );
}
