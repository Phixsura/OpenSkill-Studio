"use client";

interface ForecastPoint { month: number; projectedCost: number; confidence: number; }
interface CostForecastChartProps { forecast: ForecastPoint[]; currentMonthly: number;
  avgMonthlyGrowth: number; totalProjected: number; trend: string; }

export function CostForecastChart({ forecast, currentMonthly, avgMonthlyGrowth, totalProjected, trend }: CostForecastChartProps) {
  const trendIcon = trend === "increasing" ? "📈" : trend === "decreasing" ? "📉" : "➡️";
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💰 Cost Forecast</h3>
        <span className="text-xs text-gray-400">{trendIcon} {trend} · ${avgMonthlyGrowth}/mo</span>
      </div>
      <div className="grid grid-cols-2 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">${currentMonthly.toLocaleString()}</div>
          <div className="text-[10px] text-gray-400">Current</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">${totalProjected.toLocaleString()}</div>
          <div className="text-[10px] text-gray-400">Projected Total</div>
        </div>
      </div>
      <div className="p-3 flex gap-2">
        {forecast.map(f => (
          <div key={f.month} className="flex-1 text-center">
            <div className="text-xs font-bold">${f.projectedCost.toLocaleString()}</div>
            <div className="text-[10px] text-gray-400">M+{f.month}</div>
            <div className="text-[10px] text-gray-300">{f.confidence}% conf</div>
          </div>
        ))}
      </div>
    </div>
  );
}
