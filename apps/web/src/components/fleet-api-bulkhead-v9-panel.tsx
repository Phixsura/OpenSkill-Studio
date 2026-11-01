"use client";
export function FleetApiBulkheadV9Panel({ bulkheads, rejections }: { bulkheads: number; rejections: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧱 API Bulkhead v9</h3>
    <div className="text-sm">{bulkheads} bulkheads · {rejections} rejections</div>
  </div>);
}
