"use client";

interface UsageTrendChartProps { trend: string; changePct: number; avg: number;
  peak: number; trough: number; dataPoints: number; volatility: number; }

const TREND_STYLE: Record<string, { color: string; icon: string }> = {
  growing: { color: "text-green-600", icon: "📈" },
  declining: { color: "text-red-600", icon: "📉" },
  stable: { color: "text-gray-500", icon: "➡️" },
};

export function UsageTrendChart({ trend, changePct, avg, peak, trough, dataPoints, volatility }: UsageTrendChartProps) {
  const ts = TREND_STYLE[trend] || TREND_STYLE.stable;
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">📊 Usage Trends</h3>
        <span className={`text-sm font-medium ${ts.color}`}>{ts.icon} {trend} ({changePct > 0 ? "+" : ""}{changePct}%)</span>
      </div>
      <div className="grid grid-cols-4 gap-3 text-center">
        <div><p className="text-lg font-bold">{avg.toLocaleString()}</p><p className="text-xs text-gray-400">Average</p></div>
        <div><p className="text-lg font-bold">{peak.toLocaleString()}</p><p className="text-xs text-gray-400">Peak</p></div>
        <div><p className="text-lg font-bold">{trough.toLocaleString()}</p><p className="text-xs text-gray-400">Trough</p></div>
        <div><p className="text-lg font-bold">{volatility}%</p><p className="text-xs text-gray-400">Volatility</p></div>
      </div>
      <p className="text-xs text-gray-400 text-center mt-2">{dataPoints} data points</p>
    </div>
  );
}
