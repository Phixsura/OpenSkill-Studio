"use client";

import { useState } from "react";

interface SearchResult { type: string; title: string; url: string; }
interface PortalSearchBarProps { onSearch: (query: string) => void; results: SearchResult[]; isLoading?: boolean; }

const TYPE_ICONS: Record<string, string> = { doc: "📄", api: "🔌", community: "💬" };

export function PortalSearchBar({ onSearch, results, isLoading }: PortalSearchBarProps) {
  const [query, setQuery] = useState("");
  const [showResults, setShowResults] = useState(false);

  const handleChange = (value: string) => {
    setQuery(value);
    setShowResults(value.length >= 2);
    if (value.length >= 2) onSearch(value);
  };

  return (
    <div className="relative">
      <input value={query} onChange={e => handleChange(e.target.value)} placeholder="Search docs, APIs, community..."
        className="w-full rounded-lg border px-4 py-2.5 text-sm shadow-sm dark:border-gray-600 dark:bg-gray-700" />
      {isLoading && <span className="absolute right-3 top-3 text-xs text-gray-400">⏳</span>}
      {showResults && results.length > 0 && (
        <div className="absolute z-50 mt-1 w-full rounded-lg border bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800">
          {results.map((r, i) => (
            <a key={i} href={r.url} className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700">
              <span>{TYPE_ICONS[r.type] || "📌"}</span>
              <span>{r.title}</span>
              <span className="ml-auto text-xs text-gray-400">{r.type}</span>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
