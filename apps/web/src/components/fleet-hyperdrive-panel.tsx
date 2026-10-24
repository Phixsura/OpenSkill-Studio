"use client";
export function FleetHyperdrivePanel({ configs, active, cacheHitRate, queries }: { configs: number; active: number; cacheHitRate: number; queries: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 Hyperdrive</h3>
    <div className="text-sm">{active}/{configs} active · {cacheHitRate}% cache hit · {queries.toLocaleString()} queries</div>
  </div>);
}
