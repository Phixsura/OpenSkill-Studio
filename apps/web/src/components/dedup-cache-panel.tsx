"use client";
interface DedupCachePanelProps { size: number; hits: number; misses: number; hitRate: number; maxSize: number; }
export function DedupCachePanel({ size, hits, misses, hitRate, maxSize }: DedupCachePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Dedup Cache</h3>
        <span className={`text-xs font-bold ${hitRate >= 50 ? "text-green-600" : "text-yellow-600"}`}>
          {hitRate}% hit rate · {size}/{maxSize}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Hits</span><div className="font-bold text-green-600 text-lg">{hits.toLocaleString()}</div></div>
        <div><span className="text-gray-400">Misses</span><div className="font-bold text-lg">{misses.toLocaleString()}</div></div>
        <div><span className="text-gray-400">Size</span><div className="font-bold text-lg">{size.toLocaleString()}</div></div>
      </div>
    </div>
  );
}
