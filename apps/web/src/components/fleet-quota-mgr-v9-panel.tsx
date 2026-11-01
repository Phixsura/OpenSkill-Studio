"use client";
export function FleetQuotaMgrV9Panel({ tenants, overQuota }: { tenants: number; overQuota: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📏 Quota Manager v9</h3>
    <div className="text-sm">{tenants} tenants · {overQuota} over quota</div>
  </div>);
}
