"use client";
export function FleetAiCostV5Panel({ trackers, active, total, savings, savingsPct, forecastAcc }: { trackers: number; active: number; total: number; savings: number; savingsPct: number; forecastAcc: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Cost v5</h3>
    <div className="text-sm">{active}/{trackers} active · ${total.toLocaleString()} · ${savings.toLocaleString()} saved ({savingsPct}%) · {forecastAcc}% forecast</div>
  </div>);
}
