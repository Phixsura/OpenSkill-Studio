"use client";
export function FleetPulumiPanel({ total, upToDate, pending, failed, healthy }: { total: number; upToDate: number; pending: number; failed: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🟣 Pulumi</h3>
    <div className="text-sm">{upToDate}✅ {pending}⏳ {failed}❌ of {total}</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {failed} failed stacks</span>}
  </div>);
}
