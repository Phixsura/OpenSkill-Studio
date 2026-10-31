"use client";

interface UsageTrendChartProps { trend: string; growthPct: number; recentAvg: number;
  olderAvg: number; peak: number; trough: number; points: number; }

const TREND_STYLES: Record<string, { icon: string; color: string }> = {
  growing: { icon: "📈", color: "text-green-600" },
  declining: { icon: "📉", color: "text-red-500" },
  stable: { icon: "➡️", color: "text-blue-600" },
};

export function UsageTrendChart({ trend, growthPct, recentAvg, olderAvg, peak, trough, points }: UsageTrendChartProps) {
  const s = TREND_STYLES[trend] ?? TREND_STYLES.stable;
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Usage Trend</h3>
        <span className={`text-xs font-medium ${s.color}`}>{s.icon} {trend} ({growthPct > 0 ? "+" : ""}{growthPct}%)</span>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Recent Avg", v: recentAvg }, { l: "Previous", v: olderAvg },
          { l: "Peak", v: peak }, { l: "Trough", v: trough }].map(m => (
          <div key={m.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{m.v}</div>
            <div className="text-[9px] text-gray-400">{m.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
