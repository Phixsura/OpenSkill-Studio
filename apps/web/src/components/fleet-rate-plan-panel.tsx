"use client";
export function FleetRatePlanPanel({ total, tiers }: { total: number; tiers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Rate Plans</h3>
    <div className="text-sm">{total} tenants · {tiers} tiers</div>
  </div>);
}
