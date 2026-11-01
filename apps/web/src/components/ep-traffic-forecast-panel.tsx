"use client";
interface ForecastDay { day: number; projectedRps: number; }
interface EpTrafficForecastPanelProps { endpoint: string; forecast: ForecastDay[];
  trend: string; currentRps: number; growthRate: number; }
const TREND_COLOR: Record<string, string> = { growing: "text-green-600", declining: "text-red-500", stable: "text-gray-400" };
export function EpTrafficForecastPanel({ endpoint, forecast, trend, currentRps, growthRate }: EpTrafficForecastPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔮 Traffic Forecast: {endpoint}</h3>
        <span className={`text-xs font-bold ${TREND_COLOR[trend] ?? ""}`}>
          {trend} · {currentRps} rps · {growthRate > 0 ? "+" : ""}{growthRate}%
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {forecast.map(f => (
          <div key={f.day} className="flex justify-between px-4 py-1 text-xs">
            <span className="text-gray-400">+{f.day}d</span>
            <span>{f.projectedRps} rps</span>
          </div>
        ))}
      </div>
    </div>
  );
}
