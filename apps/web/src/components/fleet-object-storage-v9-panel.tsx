"use client";
export function FleetObjectStorageV9Panel({ buckets, sizeTb }: { buckets: number; sizeTb: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪣 Object Storage v9</h3>
    <div className="text-sm">{buckets} buckets · {sizeTb} TB</div>
  </div>);
}
