"use client";
export function FleetCapForecastPanel({ daysUntilFull, urgent, currentPct }: { daysUntilFull: number; urgent: boolean; currentPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Capacity Forecast</h3>
    <div className="text-sm">Current: {currentPct}%</div>
    {daysUntilFull > 0 ? <span className={`text-xs ${urgent ? "text-red-500" : "text-green-600"}`}>{daysUntilFull} days until full</span>
     : <span className="text-xs text-gray-400">No growth detected</span>}
  </div>);
}
