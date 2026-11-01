"use client";
export function FleetAlgoliaPanel({ indices, records, operations, avgLatency }: { indices: number; records: number; operations: number; avgLatency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔎 Algolia</h3>
    <div className="text-sm">{indices} indices · {records.toLocaleString()} records · {avgLatency}ms</div>
  </div>);
}
