"use client";
export function FleetS3Panel({ buckets, objects, sizeTb, encrypted, secure }: { buckets: number; objects: number; sizeTb: number; encrypted: number; secure: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪣 S3</h3>
    <div className="text-sm">{buckets} buckets · {objects.toLocaleString()} objects · {sizeTb}TB</div>
    {!secure && <span className="text-xs text-yellow-600">⚠️ {buckets - encrypted} unencrypted</span>}
  </div>);
}
