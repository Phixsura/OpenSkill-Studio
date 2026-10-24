"use client";

interface CdnStatsCardProps { domain: string; hitRate: number; hitRateDisplay: string;
  hits: number; misses: number; cachedPaths: number; purges: number; health: string;
  onPurge: () => void; }

export function CdnStatsCard({ domain, hitRate, hitRateDisplay, hits, misses, cachedPaths, purges, health, onPurge }: CdnStatsCardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold">🌐 CDN Cache</h3>
          <p className="text-xs text-gray-400">{domain}</p>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
          health === "good" ? "bg-green-100 text-green-700" :
          health === "fair" ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"
        }`}>{health}</span>
      </div>
      <div className="text-center mb-4">
        <p className="text-3xl font-bold">{hitRateDisplay}</p>
        <p className="text-xs text-gray-400">Cache Hit Rate</p>
      </div>
      <div className="h-3 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden mb-3">
        <div className="h-full bg-green-500 rounded-full" style={{ width: `${hitRate}%` }} />
      </div>
      <div className="grid grid-cols-4 gap-2 text-center text-xs mb-3">
        <div><p className="font-bold">{hits.toLocaleString()}</p><p className="text-gray-400">Hits</p></div>
        <div><p className="font-bold">{misses.toLocaleString()}</p><p className="text-gray-400">Misses</p></div>
        <div><p className="font-bold">{cachedPaths}</p><p className="text-gray-400">Paths</p></div>
        <div><p className="font-bold">{purges}</p><p className="text-gray-400">Purges</p></div>
      </div>
      <button onClick={onPurge}
        className="w-full py-1.5 border border-red-200 text-red-600 text-xs rounded hover:bg-red-50">Purge All</button>
    </div>
  );
}
