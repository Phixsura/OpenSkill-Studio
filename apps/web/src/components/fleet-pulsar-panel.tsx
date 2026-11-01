"use client";
export function FleetPulsarPanel({ clusters, healthy, topics, msgPerSec }: { clusters: number; healthy: number; topics: number; msgPerSec: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⭐ Pulsar</h3>
    <div className="text-sm">{healthy}/{clusters} healthy · {topics} topics · {msgPerSec.toLocaleString()} msg/s</div>
  </div>);
}
