"use client";

interface RespCacheStatsProps { totalKeys: number; active: number;
  totalHits: number; onClear: () => void; }

export function RespCacheStats({ totalKeys, active, totalHits, onClear }: RespCacheStatsProps) {
  const hitRate = totalKeys > 0 ? Math.round((totalHits / Math.max(totalKeys + totalHits, 1)) * 100) : 0;
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💨 Response Cache</h3>
        <button onClick={onClear} className="text-xs text-red-500 hover:underline">Flush</button>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Keys", v: totalKeys }, { l: "Active", v: active },
          { l: "Hits", v: totalHits }, { l: "Hit Rate", v: `${hitRate}%` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{typeof s.v === "number" ? s.v.toLocaleString() : s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
