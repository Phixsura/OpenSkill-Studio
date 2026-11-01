"use client";

interface SitemapStats { totalUrls: number; extensions: number; categories: number; developers: number; docs: number; }

export function SitemapStatsPanel({ stats, onRegenerate }: {
  stats: SitemapStats; onRegenerate?: () => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🗺️ Sitemap</h2>
        <button onClick={onRegenerate} className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg">Regenerate</button>
      </div>
      <div className="grid grid-cols-5 gap-2 text-center text-xs">
        {[
          { l: "Total URLs", v: stats.totalUrls, i: "🌐" },
          { l: "Extensions", v: stats.extensions, i: "📦" },
          { l: "Categories", v: stats.categories, i: "📂" },
          { l: "Developers", v: stats.developers, i: "👩‍💻" },
          { l: "Docs", v: stats.docs, i: "📚" },
        ].map((m) => (
          <div key={m.l} className="rounded-lg border dark:border-gray-700 p-2">
            <span className="block">{m.i}</span>
            <span className="font-bold text-lg">{m.v}</span>
            <span className="text-gray-500 block">{m.l}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
