"use client";

interface HealthTrendChart2Props { trend: string; currentAvg: number; delta: number;
  latest: number; min: number; max: number; dataPoints: number; }

const TREND_STYLES: Record<string, { icon: string; color: string }> = {
  improving: { icon: "📈", color: "text-green-600" },
  declining: { icon: "📉", color: "text-red-500" },
  stable: { icon: "➡️", color: "text-blue-600" },
};

export function HealthTrendChart2({ trend, currentAvg, delta, latest, min, max, dataPoints }: HealthTrendChart2Props) {
  const s = TREND_STYLES[trend] ?? TREND_STYLES.stable;
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Health Trend</h3>
        <span className={`text-xs font-medium ${s.color}`}>{s.icon} {trend} ({delta > 0 ? "+" : ""}{delta})</span>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Current", v: currentAvg }, { l: "Latest", v: latest },
          { l: "Min", v: min }, { l: "Max", v: max }].map(m => (
          <div key={m.l} className="bg-white dark:bg-gray-900 p-2 text-center">
            <div className="text-sm font-bold">{m.v}</div>
            <div className="text-[9px] text-gray-400">{m.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
