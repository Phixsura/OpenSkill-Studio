"use client";
export function FleetAiCostDashV3Panel({ dashboards, active, total, savings, forecasts }: { dashboards: number; active: number; total: number; savings: number; forecasts: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Cost Dashboard v3</h3>
    <div className="text-sm">{active}/{dashboards} active · ${total.toLocaleString()} total · ${savings.toLocaleString()} saved · {forecasts} forecasts</div>
  </div>);
}
