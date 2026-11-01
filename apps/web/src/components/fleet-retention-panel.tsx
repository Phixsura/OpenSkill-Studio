"use client";
export function FleetRetentionPanel({ total, compliant, overdue, allCompliant }: { total: number; compliant: number; overdue: number; allCompliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📅 Data Retention</h3>
    {allCompliant ? <span className="text-xs text-green-600">✅ All {total} datasets compliant</span>
     : <span className="text-xs text-yellow-600">⚠️ {overdue} datasets overdue for cleanup</span>}
  </div>);
}
