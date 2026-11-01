"use client";
export function FleetAiPlatRoiPanel({ trackers, active, investment, returns, roi }: { trackers: number; active: number; investment: number; returns: number; roi: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Platform ROI</h3>
    <div className="text-sm">{active}/{trackers} active · ${investment.toLocaleString()} invested · ${returns.toLocaleString()} returns · {roi}% ROI</div>
  </div>);
}
