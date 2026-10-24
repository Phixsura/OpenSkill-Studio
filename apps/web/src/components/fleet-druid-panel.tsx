"use client";
export function FleetDruidPanel({ clusters, healthy, segments, qps }: { clusters: number; healthy: number; segments: number; qps: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔮 Druid</h3>
    <div className="text-sm">{healthy}/{clusters} healthy · {segments.toLocaleString()} segments · {qps.toLocaleString()} qps</div>
  </div>);
}
