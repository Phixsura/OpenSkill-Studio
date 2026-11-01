"use client";
export function FleetResponseCacheV9Panel({ caches, hitRate }: { caches: number; hitRate: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Response Cache v9</h3>
    <div className="text-sm">{caches} caches · {hitRate}% hit rate</div>
  </div>);
}
