"use client";
export function FleetDatabaseHealthV9Panel({ databases, qps }: { databases: number; qps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗃️ Database Health v9</h3>
    <div className="text-sm">{databases} databases · {qps.toLocaleString()} qps</div>
  </div>);
}
