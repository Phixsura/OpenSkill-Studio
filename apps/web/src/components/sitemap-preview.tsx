"use client";

interface SitemapEntry { url: string; lastmod: string; changefreq: string; priority: number; }
interface SitemapPreviewProps { entries: SitemapEntry[]; sizeBytes: number; }

export function SitemapPreview({ entries, sizeBytes }: SitemapPreviewProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Sitemap</h3>
        <span className="text-xs text-gray-400">{entries.length} URLs · {(sizeBytes / 1024).toFixed(1)}KB</span>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700 max-h-56 overflow-y-auto">
        {entries.map((e, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2 text-sm">
            <span className="font-mono text-xs truncate max-w-[60%]">{e.url}</span>
            <div className="flex items-center gap-3 text-xs text-gray-400">
              <span>{e.changefreq}</span>
              <span className="font-medium">{e.priority}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
