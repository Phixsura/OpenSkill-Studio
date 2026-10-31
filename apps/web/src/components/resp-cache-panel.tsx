"use client";

interface RespCachePanelProps { entries: number; hits: number; misses: number; hitRate: number; }

export function RespCachePanel({ entries, hits, misses, hitRate }: RespCachePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💨 Response Cache</h3>
        <span className={`text-xs font-bold ${hitRate >= 80 ? "text-green-600" : "text-yellow-600"}`}>
          {hitRate}% hit rate
        </span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><div className="text-gray-400">Entries</div><div className="font-bold text-lg">{entries.toLocaleString()}</div></div>
        <div><div className="text-gray-400">Hits</div><div className="font-bold text-lg text-green-600">{hits.toLocaleString()}</div></div>
        <div><div className="text-gray-400">Misses</div><div className="font-bold text-lg text-red-500">{misses.toLocaleString()}</div></div>
      </div>
    </div>
  );
}
