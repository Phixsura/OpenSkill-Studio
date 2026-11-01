"use client";
interface DistCachePanelProps { shards: number; hits: number; misses: number;
  hitRate: number; totalKeys: number; shardSizes: Record<string, number>; }
export function DistCachePanel({ shards, hits, misses, hitRate, totalKeys, shardSizes }: DistCachePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💨 Distributed Cache</h3>
        <span className={`text-xs font-bold ${hitRate >= 80 ? "text-green-600" : "text-yellow-600"}`}>
          {hitRate}% hit · {totalKeys.toLocaleString()} keys · {shards} shards
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Hits</span><div className="font-bold text-green-600 text-lg">{hits.toLocaleString()}</div></div>
        <div><span className="text-gray-400">Misses</span><div className="font-bold text-red-500 text-lg">{misses.toLocaleString()}</div></div>
      </div>
      <div className="border-t dark:border-gray-700 flex gap-1 p-3">
        {Object.entries(shardSizes).map(([s, count]) => (
          <div key={s} className="flex-1 text-center text-[10px] text-gray-400">
            <div className="font-bold">{count}</div>
            <div>shard-{s}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
