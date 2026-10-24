"use client";
export function FleetHtmxPanel({ apps, active, swaps, avgSwap }: { apps: number; active: number; swaps: number; avgSwap: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 HTMX</h3>
    <div className="text-sm">{active}/{apps} active · {swaps.toLocaleString()} swaps · {avgSwap}ms avg</div>
  </div>);
}
