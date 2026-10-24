"use client";
export function FleetTtvPanel({ total, avgTtv, fastActivation, fastPct }: { total: number; avgTtv: number; fastActivation: number; fastPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Time to Value</h3>
    <div className="text-sm">avg {avgTtv}h · {fastActivation}/{total} under 24h ({fastPct}%)</div>
  </div>);
}
