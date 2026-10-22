"use client";

interface ErrorTrendChartProps {
  trend: "rising" | "falling" | "stable";
  avg: number;
  peak: number;
  criticalCount: number;
}

export function ErrorTrendChart({ trend, avg, peak, criticalCount }: ErrorTrendChartProps) {
  const trendConfig = {
    rising: { icon: "📈", color: "text-red-600", label: "Rising" },
    falling: { icon: "📉", color: "text-green-600", label: "Falling" },
    stable: { icon: "➡️", color: "text-gray-600", label: "Stable" },
  };
  const cfg = trendConfig[trend];

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Error Trend</h3>
        <span className={`text-sm font-medium ${cfg.color}`}>{cfg.icon} {cfg.label}</span>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-4 text-center">
        <div>
          <p className="text-xl font-bold">{avg}</p>
          <p className="text-xs text-gray-400">Avg/hour</p>
        </div>
        <div>
          <p className="text-xl font-bold">{peak}</p>
          <p className="text-xs text-gray-400">Peak</p>
        </div>
        <div>
          <p className={`text-xl font-bold ${criticalCount > 0 ? "text-red-600" : ""}`}>{criticalCount}</p>
          <p className="text-xs text-gray-400">Critical</p>
        </div>
      </div>
    </div>
  );
}
