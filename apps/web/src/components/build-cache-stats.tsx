"use client";

interface BuildCacheStatsProps { totalEntries: number; totalHits: number;
  totalSizeMb: number; avgHits: number; onClear: () => void; }

export function BuildCacheStats({ totalEntries, totalHits, totalSizeMb, avgHits, onClear }: BuildCacheStatsProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏗️ Build Cache</h3>
        <button onClick={onClear} className="text-xs text-red-500 hover:underline">Clear</button>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Entries", v: totalEntries }, { l: "Hits", v: totalHits },
          { l: "Size", v: `${totalSizeMb} MB` }, { l: "Avg Hits", v: avgHits }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
