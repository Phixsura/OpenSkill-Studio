"use client";
export function FleetHelmPanel({ total, deployed, failed, pending, healthy }: { total: number; deployed: number; failed: number; pending: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⎈ Helm Releases</h3>
    <div className="text-sm">{deployed}✅ {failed}❌ {pending}⏳ of {total}</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {failed} failed releases</span>}
  </div>);
}
