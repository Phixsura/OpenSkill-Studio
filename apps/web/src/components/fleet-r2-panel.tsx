"use client";
export function FleetR2Panel({ buckets, objects, storageGb, requests }: { buckets: number; objects: number; storageGb: number; requests: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🪣 R2</h3>
    <div className="text-sm">{buckets} buckets · {objects.toLocaleString()} objects · {storageGb}GB · {requests.toLocaleString()} req</div>
  </div>);
}
