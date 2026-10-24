"use client";

interface Prediction { month: number; predicted: number; }
interface UsageForecastChartProps { trend: string; growthRatePct: number;
  predictions: Prediction[]; historicalPoints: number; slope: number; }

const TREND_STYLE: Record<string, { color: string; icon: string }> = {
  growing: { color: "text-green-600", icon: "📈" },
  declining: { color: "text-red-600", icon: "📉" },
  flat: { color: "text-gray-500", icon: "➡️" },
};

export function UsageForecastChart({ trend, growthRatePct, predictions, historicalPoints, slope }: UsageForecastChartProps) {
  const t = TREND_STYLE[trend] || TREND_STYLE.flat;
  const maxVal = Math.max(...predictions.map(p => p.predicted), 1);
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🔮 Usage Forecast</h3>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-medium ${t.color}`}>{t.icon} {trend}</span>
          <span className="text-xs text-gray-400">{growthRatePct}%/mo</span>
        </div>
      </div>
      <div className="flex items-end gap-1 h-20 mb-2">
        {predictions.map(p => (
          <div key={p.month} className="flex-1 flex flex-col items-center justify-end">
            <div className="w-full bg-blue-400 rounded-t opacity-60" style={{ height: `${(p.predicted / maxVal) * 100}%` }} />
            <span className="text-[10px] text-gray-400 mt-1">+{p.month}</span>
          </div>
        ))}
      </div>
      <div className="flex justify-between text-xs text-gray-400">
        <span>{historicalPoints} historical points</span>
        <span>Forecast: {predictions[predictions.length - 1]?.predicted.toLocaleString()}</span>
      </div>
    </div>
  );
}
