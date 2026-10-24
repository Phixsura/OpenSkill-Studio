"use client";
export function FleetCacheEvictPanel({ totalEvictions, highEviction, needsResize }: { totalEvictions: number; highEviction: number; needsResize: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗑️ Cache Evictions</h3>
    <div className="text-sm">{totalEvictions}/s total</div>
    {needsResize && <span className="text-xs text-yellow-600">⚠️ {highEviction} caches need resizing</span>}
  </div>);
}
