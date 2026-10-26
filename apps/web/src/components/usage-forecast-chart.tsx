"use client";

interface ForecastPoint {
  period: string;
  actual?: number;
  predicted?: number;
  confidence: number;
}

export function UsageForecastChart({
  data,
  metricName,
  unit,
  trend,
  growthRate,
}: {
  data: ForecastPoint[];
  metricName: string;
  unit: string;
  trend: "growing" | "stable" | "declining";
  growthRate: number;
}) {
  const maxVal = Math.max(...data.map((d) => Math.max(d.actual || 0, d.predicted || 0)));
  const trendConfig = {
    growing: { icon: "📈", color: "text-green-500", label: "Growing" },
    stable: { icon: "➡️", color: "text-blue-500", label: "Stable" },
    declining: { icon: "📉", color: "text-red-500", label: "Declining" },
  };
  const tcfg = trendConfig[trend];

  return (
    <div className="rounded-xl border dark:border-gray-700 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📊 {metricName} Forecast</h2>
        <div className="flex items-center gap-2">
          <span className={tcfg.color}>{tcfg.icon} {tcfg.label}</span>
          <span className="text-xs text-gray-400">({growthRate > 0 ? "+" : ""}{growthRate}%)</span>
        </div>
      </div>

      {/* Simple bar chart */}
      <div className="flex items-end gap-1 h-40">
        {data.map((point, i) => {
          const val = point.actual ?? point.predicted ?? 0;
          const height = maxVal > 0 ? (val / maxVal) * 100 : 0;
          const isForecast = point.predicted !== undefined && point.actual === undefined;
          return (
            <div key={i} className="flex-1 flex flex-col items-center gap-1">
              <div className="text-xs text-gray-400">{val.toLocaleString()}</div>
              <div className="w-full relative" style={{ height: `${height}%`, minHeight: "4px" }}>
                <div className={`w-full h-full rounded-t ${
                  isForecast ? "bg-blue-300/50 dark:bg-blue-700/30 border border-dashed border-blue-400" : "bg-blue-500"
                }`} />
              </div>
              <div className="text-xs text-gray-400 truncate w-full text-center">{point.period}</div>
            </div>
          );
        })}
      </div>

      <div className="flex items-center gap-4 text-xs text-gray-400">
        <div className="flex items-center gap-1"><div className="w-3 h-3 bg-blue-500 rounded" /> Actual</div>
        <div className="flex items-center gap-1"><div className="w-3 h-3 bg-blue-300/50 border border-dashed border-blue-400 rounded" /> Forecast</div>
        <span>Unit: {unit}</span>
      </div>
    </div>
  );
}
