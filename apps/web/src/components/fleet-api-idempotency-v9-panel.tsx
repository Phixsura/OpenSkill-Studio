"use client";
export function FleetApiIdempotencyV9Panel({ endpoints, duplicates }: { endpoints: number; duplicates: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔁 API Idempotency v9</h3>
    <div className="text-sm">{endpoints} endpoints · {duplicates} duplicates caught</div>
  </div>);
}
