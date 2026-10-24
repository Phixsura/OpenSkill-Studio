"use client";
export function FleetFastifyPanel({ instances, healthy, rps, p95 }: { instances: number; healthy: number; rps: number; p95: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Fastify</h3>
    <div className="text-sm">{healthy}/{instances} healthy · {rps.toLocaleString()} rps · p95 {p95}ms</div>
  </div>);
}
