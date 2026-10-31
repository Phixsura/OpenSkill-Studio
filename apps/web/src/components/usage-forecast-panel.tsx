"use client";
interface UsageForecastPanelProps { currentDaily: number; projected30d: number;
  trend: string; growthRatePct: number; }
const TREND_COLOR: Record<string, string> = { growing: "text-green-600", declining: "text-red-500", stable: "text-gray-400" };
export function UsageForecastPanel({ currentDaily, projected30d, trend, growthRatePct }: UsageForecastPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔮 Usage Forecast</h3>
        <span className={`text-xs font-bold ${TREND_COLOR[trend] ?? ""}`}>
          {trend} · {growthRatePct > 0 ? "+" : ""}{growthRatePct}%
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Current</span><div className="font-bold text-lg">{currentDaily.toLocaleString()}/day</div></div>
        <div><span className="text-gray-400">30d Projected</span><div className="font-bold text-lg">{projected30d.toLocaleString()}/day</div></div>
      </div>
    </div>
  );
}
