"use client";
export function FleetRetryStormPanel({ total, amplifying, maxRatio, storm }: { total: number; amplifying: number; maxRatio: number; storm: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌪️ Retry Storm</h3>
    {storm ? <span className="text-xs text-red-500">🚨 Retry storm! {amplifying} services amplifying (max {maxRatio}x)</span>
     : <span className="text-xs text-green-600">✅ No retry storm</span>}
  </div>);
}
