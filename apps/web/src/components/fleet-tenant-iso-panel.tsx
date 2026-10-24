"use client";
export function FleetTenantIsoPanel({ total, isolated, shared, fullyIsolated }: { total: number; isolated: number; shared: number; fullyIsolated: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏠 Tenant Isolation</h3>
    {fullyIsolated ? <span className="text-xs text-green-600">✅ All {total} fully isolated</span>
     : <span className="text-xs text-yellow-600">⚠️ {shared} shared tenants</span>}
  </div>);
}
