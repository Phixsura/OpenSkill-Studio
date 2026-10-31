"use client";

interface CdnRegion { region: string; hitRate: number; requests: number; }
interface CdnOptimizerPanelProps { hitRate: number; hits: number; misses: number;
  bandwidthSavedMb: number; regions: CdnRegion[]; }

export function CdnOptimizerPanel({ hitRate, hits, misses, bandwidthSavedMb, regions }: CdnOptimizerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌍 CDN Performance</h3>
        <span className={`text-xs font-bold ${hitRate >= 90 ? "text-green-600" : hitRate >= 70 ? "text-yellow-600" : "text-red-500"}`}>
          {hitRate}% hit rate · {bandwidthSavedMb}MB saved
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><div className="text-gray-400">Hits</div><div className="font-bold text-green-600 text-lg">{hits.toLocaleString()}</div></div>
        <div><div className="text-gray-400">Misses</div><div className="font-bold text-red-500 text-lg">{misses.toLocaleString()}</div></div>
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {regions.map(r => (
          <div key={r.region} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-semibold">{r.region}</span>
            <span className="text-gray-400">{r.hitRate}% · {r.requests.toLocaleString()} reqs</span>
          </div>
        ))}
      </div>
    </div>
  );
}
