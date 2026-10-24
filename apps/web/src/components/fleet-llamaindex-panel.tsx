"use client";
export function FleetLlamaindexPanel({ apps, active, indexes, queries }: { apps: number; active: number; indexes: number; queries: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🦙 LlamaIndex</h3>
    <div className="text-sm">{active}/{apps} active · {indexes} indexes · {queries.toLocaleString()} queries</div>
  </div>);
}
