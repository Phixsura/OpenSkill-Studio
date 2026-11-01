"use client";
export function FleetCacheInvalidationV9Panel({ caches, invalidations }: { caches: number; invalidations: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗑️ Cache Invalidation v9</h3>
    <div className="text-sm">{caches} caches · {invalidations} invalidations</div>
  </div>);
}
