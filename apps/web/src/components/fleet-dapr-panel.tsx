"use client";
export function FleetDaprPanel({ total, healthy, components, allHealthy }: { total: number; healthy: number; components: number; allHealthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 Dapr</h3>
    <div className="text-sm">{healthy}/{total} healthy · {components} components</div>
    {!allHealthy && <span className="text-xs text-red-500">⚠️ Unhealthy sidecars</span>}
  </div>);
}
