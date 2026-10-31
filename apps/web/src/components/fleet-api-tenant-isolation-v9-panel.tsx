"use client";
export function FleetApiTenantIsolationV9Panel({ tenants, violations }: { tenants: number; violations: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏢 Tenant Isolation v9</h3>
    <div className="text-sm">{tenants} tenants · {violations} violations</div>
  </div>);
}
