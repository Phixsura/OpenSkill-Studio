"use client";
export function FleetScylladbPanel({ nodes, up, opsPerSec, p99 }: { nodes: number; up: number; opsPerSec: number; p99: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🦂 ScyllaDB</h3>
    <div className="text-sm">{up}/{nodes} up · {opsPerSec.toLocaleString()} ops/s · p99 {p99}ms</div>
  </div>);
}
