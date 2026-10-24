"use client";
export function FleetKvStoreV9Panel({ clusters, ops }: { clusters: number; ops: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔑 KV Store v9</h3>
    <div className="text-sm">{clusters} clusters · {ops.toLocaleString()} ops/s</div>
  </div>);
}
