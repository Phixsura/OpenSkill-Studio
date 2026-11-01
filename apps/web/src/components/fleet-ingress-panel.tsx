"use client";
export function FleetIngressPanel({ totalRps, routes, errorRoutes, healthy }: { totalRps: number; routes: number; errorRoutes: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚪 Fleet Ingress</h3>
    <div className="text-sm">{totalRps.toLocaleString()} rps · {routes} routes</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {errorRoutes} high-error routes</span>}
  </div>);
}
