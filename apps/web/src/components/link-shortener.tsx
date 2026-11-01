"use client";

import { useState } from "react";

interface ShortLink { slug: string; original: string; clicks: number; }
interface LinkShortenerProps { links: ShortLink[]; totalClicks: number; onShorten: (url: string) => void; }

export function LinkShortener({ links, totalClicks, onShorten }: LinkShortenerProps) {
  const [url, setUrl] = useState("");
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">Short Links</h3>
      <div className="flex gap-2">
        <input type="url" placeholder="https://..." value={url} onChange={e => setUrl(e.target.value)}
          className="flex-1 rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
        <button onClick={() => { if (url) { onShorten(url); setUrl(""); } }}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Shorten</button>
      </div>
      <p className="text-xs text-gray-400">{totalClicks.toLocaleString()} total clicks across {links.length} links</p>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {links.map(l => (
          <div key={l.slug} className="flex items-center justify-between px-4 py-2.5">
            <div className="min-w-0">
              <p className="text-sm font-mono text-blue-600">osk.li/{l.slug}</p>
              <p className="text-xs text-gray-400 truncate">{l.original}</p>
            </div>
            <span className="text-sm font-medium">{l.clicks.toLocaleString()} clicks</span>
          </div>
        ))}
      </div>
    </div>
  );
}
