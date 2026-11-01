"use client";

interface SparklineChartProps { polyline: string; width: number; height: number;
  trend: string; current: number; changePct: number; label?: string; }

export function SparklineChart({ polyline, width, height, trend, current, changePct, label }: SparklineChartProps) {
  const color = trend === "up" ? "#22C55E" : trend === "down" ? "#EF4444" : "#6B7280";
  return (
    <div className="inline-flex items-center gap-2">
      {label && <span className="text-xs text-gray-400">{label}</span>}
      <svg width={width} height={height} className="overflow-visible">
        <polyline points={polyline} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <div className="text-right">
        <span className="text-sm font-bold">{current}</span>
        <span className={`text-xs ml-1 ${trend === "up" ? "text-green-600" : trend === "down" ? "text-red-600" : "text-gray-400"}`}>
          {changePct > 0 ? "+" : ""}{changePct}%
        </span>
      </div>
    </div>
  );
}
