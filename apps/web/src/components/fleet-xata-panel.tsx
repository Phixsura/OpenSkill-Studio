"use client";
export function FleetXataPanel({ databases, active, branches, records }: { databases: number; active: number; branches: number; records: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔷 Xata</h3>
    <div className="text-sm">{active}/{databases} active · {branches} branches · {records.toLocaleString()} records</div>
  </div>);
}
