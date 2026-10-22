"use client";

import { useState } from "react";

interface SearchResult { type: string; title: string; url: string; }
interface PortalSearchBarProps { onSearch: (query: string) => void; results: SearchResult[]; }

const TYPE_ICONS: Record<string, string> = { app: "📦", doc: "📖", event: "🔔", setting: "⚙️" };

export function PortalSearchBar({ onSearch, results }: PortalSearchBarProps) {
  const [query, setQuery] = useState("");
  const [focused, setFocused] = useState(false);
  return (
    <div className="relative">
      <input value={query} onChange={e => { setQuery(e.target.value); onSearch(e.target.value); }}
        onFocus={() => setFocused(true)} onBlur={() => setTimeout(() => setFocused(false), 200)}
        placeholder="Search apps, docs, events..."
        className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm dark:border-gray-600 dark:bg-gray-800" />
      {focused && query && results.length > 0 && (
        <div className="absolute z-20 mt-1 w-full rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-900">
          {results.map((r, i) => (
            <a key={i} href={r.url} className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-800">
              <span>{TYPE_ICONS[r.type] ?? "•"}</span>{r.title}
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
