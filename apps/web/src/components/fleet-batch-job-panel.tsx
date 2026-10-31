"use client";
export function FleetBatchJobPanel({ total, completed, failed, avgDuration, reliable }: { total: number; completed: number; failed: number; avgDuration: number; reliable: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚙️ Batch Jobs</h3>
    <div className="text-sm">{completed}✅ {failed}❌ · avg {avgDuration}min</div>
    {!reliable && <span className="text-xs text-red-500">⚠️ Job failures detected</span>}
  </div>);
}
