"use client";
export function FleetRunbookAutoV9Panel({ total, successRate }: { total: number; successRate: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📖 Runbook Automation v9</h3>
    <div className="text-sm">{total} runbooks · {successRate}% success</div>
  </div>);
}
