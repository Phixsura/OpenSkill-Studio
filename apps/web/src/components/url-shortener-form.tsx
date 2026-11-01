"use client";
import { useState } from "react";

interface ShortLink { shortUrl: string; slug: string; original: string; clicks: number; }
interface UrlShortenerFormProps { links: ShortLink[];
  onShorten: (url: string, slug: string) => void; }

export function UrlShortenerForm({ links, onShorten }: UrlShortenerFormProps) {
  const [url, setUrl] = useState("");
  const [slug, setSlug] = useState("");
  const handleSubmit = () => { if (url) { onShorten(url, slug); setUrl(""); setSlug(""); } };
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🔗 URL Shortener</h3>
      <div className="flex gap-2 mb-4">
        <input value={url} onChange={e => setUrl(e.target.value)} placeholder="https://..."
          className="flex-1 text-sm px-3 py-1.5 border rounded dark:bg-gray-800 dark:border-gray-600" />
        <input value={slug} onChange={e => setSlug(e.target.value)} placeholder="custom-slug"
          className="w-28 text-sm px-2 py-1.5 border rounded dark:bg-gray-800 dark:border-gray-600" />
        <button onClick={handleSubmit}
          className="px-4 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">Shorten</button>
      </div>
      {links.length > 0 && (
        <div className="space-y-1">
          {links.map(l => (
            <div key={l.slug} className="flex justify-between text-xs bg-gray-50 dark:bg-gray-800 rounded px-3 py-1.5">
              <a href={l.shortUrl} className="text-blue-600 font-mono">{l.shortUrl}</a>
              <span className="text-gray-400">{l.clicks} clicks</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
