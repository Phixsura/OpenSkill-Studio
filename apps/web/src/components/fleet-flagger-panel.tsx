"use client";
export function FleetFlaggerPanel({ total, progressing, succeeded, failed, healthy }: { total: number; progressing: number; succeeded: number; failed: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 Flagger</h3>
    <div className="text-sm">{succeeded}✅ {progressing}🔄 {failed}❌</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {failed} failed canaries</span>}
  </div>);
}
