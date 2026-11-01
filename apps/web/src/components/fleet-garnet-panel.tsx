"use client";
export function FleetGarnetPanel({ instances, healthy, opsPerSec, p99Us }: { instances: number; healthy: number; opsPerSec: number; p99Us: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💎 Garnet</h3>
    <div className="text-sm">{healthy}/{instances} healthy · {opsPerSec.toLocaleString()} ops/s · p99 {p99Us}μs</div>
  </div>);
}
