"use client";
export function FleetSvcDiscPanel({ total, resolvable, staleDns, healthy }: { total: number; resolvable: number; staleDns: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 Service Discovery</h3>
    <div className="text-sm">{resolvable}/{total} resolvable</div>
    {!healthy && <span className="text-xs text-yellow-600">⚠️ {staleDns} stale DNS entries</span>}
  </div>);
}
