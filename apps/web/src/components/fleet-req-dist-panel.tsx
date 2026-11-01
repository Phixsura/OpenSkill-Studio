"use client";
export function FleetReqDistPanel({ totalRequests, regions, hotspot }: { totalRequests: number; regions: number; hotspot: string | null; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗺️ Request Distribution</h3>
    <div className="text-sm">{totalRequests.toLocaleString()} total · {regions} regions</div>
    {hotspot && <div className="text-xs text-blue-500">🔥 Hotspot: {hotspot}</div>}
  </div>);
}
