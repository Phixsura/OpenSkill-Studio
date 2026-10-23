"use client";

interface SparklineWidgetProps { points: number[]; label: string; current: number;
  change: number; changePct: number; trend: string; }

export function SparklineWidget({ points, label, current, change, changePct, trend }: SparklineWidgetProps) {
  const trendIcon = trend === "up" ? "↑" : trend === "down" ? "↓" : "→";
  const trendColor = trend === "up" ? "text-green-500" : trend === "down" ? "text-red-500" : "text-gray-400";
  return (
    <div className="flex items-center gap-3 rounded-lg border p-3 dark:border-gray-700">
      <div className="flex-1">
        <p className="text-xs text-gray-400">{label}</p>
        <div className="flex items-baseline gap-1">
          <span className="text-lg font-bold">{current.toLocaleString()}</span>
          <span className={`text-xs ${trendColor}`}>{trendIcon} {Math.abs(changePct)}%</span>
        </div>
      </div>
      <div className="flex h-8 w-20 items-end gap-px">
        {points.map((p, i) => (
          <div key={i} className="flex-1 rounded-t bg-blue-400 dark:bg-blue-600"
            style={{ height: `${Math.max(p, 5)}%`, opacity: 0.4 + (i / points.length) * 0.6 }} />
        ))}
      </div>
    </div>
  );
}
