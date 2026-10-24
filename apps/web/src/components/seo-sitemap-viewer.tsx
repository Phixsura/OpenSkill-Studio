"use client";

interface SitemapUrl { loc: string; priority: number; changefreq: string; lastmod?: string; }
interface SeoSitemapViewerProps { urls: SitemapUrl[]; totalUrls: number;
  staticPages: number; dynamicPages: number; onGenerate: () => void; }

export function SeoSitemapViewer({ urls, totalUrls, staticPages, dynamicPages, onGenerate }: SeoSitemapViewerProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Sitemap</h2>
        <button onClick={onGenerate} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Regenerate</button>
      </div>
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold">{totalUrls}</p><p className="text-xs text-gray-400">Total URLs</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold">{staticPages}</p><p className="text-xs text-gray-400">Static</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-lg font-bold">{dynamicPages}</p><p className="text-xs text-gray-400">Dynamic</p>
        </div>
      </div>
      <div className="max-h-48 overflow-y-auto space-y-0.5">
        {urls.slice(0, 20).map((u, i) => (
          <div key={i} className="flex items-center justify-between rounded border px-2 py-1 font-mono text-xs dark:border-gray-700">
            <span className="truncate text-blue-500">{u.loc}</span>
            <span className="text-gray-400">{u.priority}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
