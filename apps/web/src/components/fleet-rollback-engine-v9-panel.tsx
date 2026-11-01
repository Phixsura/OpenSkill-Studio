"use client";
export function FleetRollbackEngineV9Panel({ total, avgTime }: { total: number; avgTime: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏪ Rollback Engine v9</h3>
    <div className="text-sm">{total} rollbacks · {avgTime}s avg</div>
  </div>);
}
