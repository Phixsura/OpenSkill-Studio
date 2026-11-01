"use client";

interface GeoEntry { region: string; name: string; count: number; pct: number; }
interface GeoDistributionMapProps { distribution: GeoEntry[]; total: number; topRegion: string | null; }

export function GeoDistributionMap({ distribution, total, topRegion }: GeoDistributionMapProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌍 Geo Distribution</h3>
        <span className="text-xs text-gray-400">{total.toLocaleString()} requests · {distribution.length} regions</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {distribution.map(g => (
          <div key={g.region} className="px-4 py-2.5">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{g.name}</span>
                {g.region === topRegion && <span className="text-[10px] text-blue-500">📍 top</span>}
              </div>
              <span className="text-xs text-gray-400">{g.count.toLocaleString()} ({g.pct}%)</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${g.pct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
