"use client";

interface SitemapPage { path: string; lastmod?: string; priority: number; }
interface SitemapPreviewProps { pages: SitemapPage[]; baseUrl: string; onGenerate: () => void; }

export function SitemapPreview({ pages, baseUrl, onGenerate }: SitemapPreviewProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Sitemap</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{pages.length} URLs</span>
          <button onClick={onGenerate} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Generate</button>
        </div>
      </div>
      <div className="space-y-1">
        {pages.map(p => (
          <div key={p.path} className="flex items-center justify-between rounded border px-3 py-1.5 font-mono text-xs dark:border-gray-700">
            <span className="text-blue-500">{baseUrl}{p.path}</span>
            <div className="flex gap-3 text-gray-400">
              {p.lastmod && <span>{p.lastmod}</span>}
              <span>pri: {p.priority}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
