"use client";

import { useState } from "react";

interface ShortLink { short_url: string; original_url: string; slug: string; clicks: number; }
interface UrlShortenerPanelProps { links: ShortLink[]; totalClicks: number;
  onCreate: (url: string, slug?: string) => void; onCopy: (url: string) => void; }

export function UrlShortenerPanel({ links, totalClicks, onCreate, onCopy }: UrlShortenerPanelProps) {
  const [url, setUrl] = useState("");

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Short Links</h2>
        <span className="text-xs text-gray-400">{totalClicks.toLocaleString()} total clicks</span>
      </div>
      <div className="flex gap-2">
        <input value={url} onChange={e => setUrl(e.target.value)} placeholder="https://..."
          className="flex-1 rounded border px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700" />
        <button onClick={() => { onCreate(url); setUrl(""); }}
          className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Shorten</button>
      </div>
      <div className="space-y-1.5">
        {links.map(l => (
          <div key={l.slug} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
            <div>
              <p className="font-mono text-sm text-blue-500">{l.short_url}</p>
              <p className="truncate text-xs text-gray-400">{l.original_url}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">{l.clicks} clicks</span>
              <button onClick={() => onCopy(l.short_url)} className="text-xs text-blue-500">Copy</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
