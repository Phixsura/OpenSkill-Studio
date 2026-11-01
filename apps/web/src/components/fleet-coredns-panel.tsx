"use client";
export function FleetCorednsPanel({ instances, healthy, qps, cacheHitPct }: { instances: number; healthy: number; qps: number; cacheHitPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 CoreDNS</h3>
    <div className="text-sm">{healthy}/{instances} healthy · {qps.toLocaleString()} qps · {cacheHitPct}% cache hit</div>
  </div>);
}
