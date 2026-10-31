"use client";
export function FleetNginxPanel({ controllers, activeConns, rps, errors5xx, healthy }: { controllers: number; activeConns: number; rps: number; errors5xx: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 NGINX</h3>
    <div className="text-sm">{rps.toLocaleString()} rps · {activeConns.toLocaleString()} conns</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {errors5xx} 5xx errors</span>}
  </div>);
}
