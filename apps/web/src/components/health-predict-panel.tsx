"use client";
interface Forecast { period: number; projected: number; }
interface HealthPredictPanelProps { forecast: Forecast[]; trend: string; current: number;
  willBreachSla: boolean; }
const TREND_STYLE: Record<string, string> = { improving: "text-green-600", declining: "text-red-500", stable: "text-gray-400" };
export function HealthPredictPanel({ forecast, trend, current, willBreachSla }: HealthPredictPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔮 Health Prediction</h3>
        <span className={`text-xs font-bold ${TREND_STYLE[trend] ?? ""}`}>
          {trend} · current: {current}%{willBreachSla ? " · ⚠ SLA at risk" : ""}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {forecast.map(f => (
          <div key={f.period} className="flex justify-between px-4 py-1 text-xs">
            <span className="text-gray-400">+{f.period}d</span>
            <span className={f.projected < 99 ? "text-red-500" : "text-green-600"}>{f.projected}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
