"use client";

interface CacheStatsCardProps { totalKeys: number; active: number;
  expired: number; totalHits: number; onClear: () => void; }

export function CacheStatsCard({ totalKeys, active, expired, totalHits, onClear }: CacheStatsCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💨 Cache Stats</h3>
        <button onClick={onClear} className="text-xs text-red-500 hover:underline">Clear All</button>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {[
          { label: "Total Keys", value: totalKeys },
          { label: "Active", value: active },
          { label: "Expired", value: expired },
          { label: "Total Hits", value: totalHits },
        ].map(s => (
          <div key={s.label} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{s.value.toLocaleString()}</div>
            <div className="text-[10px] text-gray-400">{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
