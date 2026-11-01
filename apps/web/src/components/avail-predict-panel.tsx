"use client";
interface Forecast { day: number; projectedPct: number; }
interface AvailPredictPanelProps { forecast: Forecast[]; trend: string; currentPct: number; willBreach: boolean; }
const TREND_COLOR: Record<string, string> = { improving: "text-green-600", declining: "text-red-500", stable: "text-gray-400" };
export function AvailPredictPanel({ forecast, trend, currentPct, willBreach }: AvailPredictPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔮 Availability Prediction</h3>
        <span className={`text-xs font-bold ${TREND_COLOR[trend] ?? ""}`}>
          {trend} · {currentPct}%{willBreach ? " · ⚠ breach risk" : ""}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {forecast.map(f => (
          <div key={f.day} className="flex justify-between px-4 py-1 text-xs">
            <span className="text-gray-400">+{f.day}d</span>
            <span className={f.projectedPct < 99 ? "text-red-500" : "text-green-600"}>{f.projectedPct}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
