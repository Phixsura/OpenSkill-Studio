"use client";

interface GrowthMetric { first: number; last: number; growthPct: number; trend: string; }
interface GrowthTrackerProps { metrics: Record<string, GrowthMetric>; overall: string; periods: number; }

const TREND_ICONS: Record<string, string> = { up: "📈", down: "📉", flat: "➡️" };

export function GrowthTracker({ metrics, overall, periods }: GrowthTrackerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Platform Growth</h3>
        <span className={`text-xs ${overall === "growing" ? "text-green-600" : "text-yellow-600"}`}>
          {overall} · {periods} periods
        </span>
      </div>
      <div className="grid grid-cols-2 gap-px bg-gray-200 dark:bg-gray-700">
        {Object.entries(metrics).map(([key, m]) => (
          <div key={key} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{TREND_ICONS[m.trend]} {m.growthPct > 0 ? "+" : ""}{m.growthPct}%</div>
            <div className="text-[9px] text-gray-400 capitalize">{key.replaceAll("_", " ")}</div>
            <div className="text-[10px] text-gray-400">{m.first.toLocaleString()} → {m.last.toLocaleString()}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
