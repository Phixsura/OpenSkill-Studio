"use client";
export function FleetApiBatchV9Panel({ batches, processed }: { batches: number; processed: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 API Batch v9</h3>
    <div className="text-sm">{batches} batches · {processed.toLocaleString()} processed</div>
  </div>);
}
