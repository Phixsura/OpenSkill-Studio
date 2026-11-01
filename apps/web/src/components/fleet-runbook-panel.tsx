"use client";
export function FleetRunbookPanel({ total, success, failed, successRate }: { total: number; success: number; failed: number; successRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📖 Runbook Automation</h3>
    <div className="text-sm">{success}✅ {failed}❌ of {total} · {successRate}%</div>
  </div>);
}
