"use client";

interface SitemapStatsCardProps { totalUrls: number; staticCount: number; dynamicCount: number;
  lastGenerated: string; onRegenerate: () => void; }

export function SitemapStatsCard({ totalUrls, staticCount, dynamicCount, lastGenerated, onRegenerate }: SitemapStatsCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Sitemap</h3>
        <button onClick={onRegenerate} className="rounded border px-3 py-1 text-xs hover:bg-gray-50 dark:border-gray-600">
          🔄 Regenerate
        </button>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-3 text-center">
        <div><p className="text-xl font-bold">{totalUrls}</p><p className="text-xs text-gray-400">Total URLs</p></div>
        <div><p className="text-xl font-bold">{staticCount}</p><p className="text-xs text-gray-400">Static</p></div>
        <div><p className="text-xl font-bold">{dynamicCount}</p><p className="text-xs text-gray-400">Dynamic</p></div>
      </div>
      <p className="mt-2 text-xs text-gray-400">Last generated: {lastGenerated}</p>
    </div>
  );
}
