"use client";
export function FleetMigrationRunnerV9Panel({ total, pending }: { total: number; pending: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Migration Runner v9</h3>
    <div className="text-sm">{total} migrations · {pending} pending</div>
  </div>);
}
