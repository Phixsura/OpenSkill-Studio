"use client";
export function FleetMultiTenantV9Panel({ tenants, noisy }: { tenants: number; noisy: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏢 Multi-Tenant v9</h3>
    <div className="text-sm">{tenants} tenants · {noisy} noisy neighbors</div>
  </div>);
}
