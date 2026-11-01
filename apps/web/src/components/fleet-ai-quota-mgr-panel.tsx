"use client";
export function FleetAiQuotaMgrPanel({ quotas, active, tenants, enforced, throttled }: { quotas: number; active: number; tenants: number; enforced: number; throttled: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Quota Manager</h3>
    <div className="text-sm">{active}/{quotas} active · {tenants} tenants · {enforced} enforced · {throttled} throttled</div>
  </div>);
}
