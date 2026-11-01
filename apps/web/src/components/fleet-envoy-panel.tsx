"use client";
export function FleetEnvoyPanel({ total, live, draining, totalRps }: { total: number; live: number; draining: number; totalRps: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔀 Envoy</h3>
    <div className="text-sm">{live}/{total} live · {draining} draining · {totalRps.toLocaleString()} rps</div>
  </div>);
}
