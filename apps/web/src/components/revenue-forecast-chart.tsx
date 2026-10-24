"use client";

interface Projection { month: number; projected_revenue: number; confidence: number; }
interface RevenueForecastChartProps { lastMonth: number; avgGrowthRate: number;
  projections: Projection[]; totalHistorical: number; totalProjected: number; }

export function RevenueForecastChart({ lastMonth, avgGrowthRate, projections, totalHistorical, totalProjected }: RevenueForecastChartProps) {
  const allValues = [lastMonth, ...projections.map(p => p.projected_revenue)];
  const maxVal = Math.max(...allValues, 1);
  const trend = avgGrowthRate >= 0 ? "📈" : "📉";

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Revenue Forecast {trend}</h2>
        <span className={`text-sm font-medium ${avgGrowthRate >= 0 ? "text-green-600" : "text-red-600"}`}>
          {avgGrowthRate >= 0 ? "+" : ""}{avgGrowthRate}% avg
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-lg bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-lg font-bold">${totalHistorical.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Historical Total</p>
        </div>
        <div className="rounded-lg bg-blue-50 p-3 text-center dark:bg-blue-900/10">
          <p className="text-lg font-bold text-blue-600">${totalProjected.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Projected</p>
        </div>
      </div>
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="w-16 text-xs text-gray-400">Current</span>
          <div className="h-5 flex-1 rounded bg-green-500" style={{ width: `${(lastMonth / maxVal) * 100}%` }} />
          <span className="w-20 text-right text-xs font-medium">${lastMonth.toLocaleString()}</span>
        </div>
        {projections.map(p => (
          <div key={p.month} className="flex items-center gap-2">
            <span className="w-16 text-xs text-gray-400">+{p.month}mo</span>
            <div className="h-5 flex-1 rounded bg-blue-400 opacity-75"
              style={{ width: `${(p.projected_revenue / maxVal) * 100}%`, opacity: p.confidence }} />
            <span className="w-20 text-right text-xs font-medium">${p.projected_revenue.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
