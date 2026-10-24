"use client";
export function FleetAiKvCachePanel({ caches, active, sizeGb, hitRate, evictions }: { caches: number; active: number; sizeGb: number; hitRate: number; evictions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗃️ AI KV Cache</h3>
    <div className="text-sm">{active}/{caches} active · {sizeGb}GB · {hitRate}% hit · {evictions.toLocaleString()} evictions</div>
  </div>);
}
