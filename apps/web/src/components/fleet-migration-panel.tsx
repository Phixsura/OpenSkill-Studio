"use client";
export function FleetMigrationPanel({ total, current, pending, totalPending, allCurrent }: { total: number; current: number; pending: number; totalPending: number; allCurrent: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 DB Migrations</h3>
    {allCurrent ? <span className="text-xs text-green-600">✅ All {total} DBs current</span>
     : <span className="text-xs text-yellow-600">⚠️ {totalPending} pending across {pending} DBs</span>}
  </div>);
}
