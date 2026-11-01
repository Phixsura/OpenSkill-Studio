"use client";

import { useState } from "react";

interface SearchResult { extensionId: string; name: string; description: string; category: string; rating: number; installs: number; tags: string[]; }
interface Facets { categories: Record<string, number>; tags: Record<string, number>; }

export function ExtensionSearchPanel({
  results, facets, suggestions, onSearch, onAutocomplete,
}: {
  results: SearchResult[]; facets: Facets; suggestions: string[];
  onSearch?: (query: string, category?: string) => void;
  onAutocomplete?: (prefix: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [cat, setCat] = useState<string>("");

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🔍 Extension Search</h2>
      <div className="flex gap-2">
        <input type="text" value={query} onChange={(e) => { setQuery(e.target.value); onAutocomplete?.(e.target.value); }}
          placeholder="Search extensions..."
          className="flex-1 rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm" />
        <button onClick={() => onSearch?.(query, cat || undefined)}
          className="text-sm bg-blue-600 text-white px-4 py-2 rounded-lg">Search</button>
      </div>

      {suggestions.length > 0 && query && (
        <div className="flex gap-1 flex-wrap">
          {suggestions.map((s) => (
            <button key={s} onClick={() => { setQuery(s); onSearch?.(s); }}
              className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">{s}</button>
          ))}
        </div>
      )}

      <div className="space-y-1">
        {results.map((r) => (
          <div key={r.extensionId} className="rounded-xl border dark:border-gray-700 p-3">
            <div className="flex items-center justify-between mb-1">
              <span className="font-semibold text-sm">{r.name}</span>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-yellow-500">★ {r.rating}</span>
                <span className="text-gray-400">{r.installs.toLocaleString()} installs</span>
              </div>
            </div>
            <p className="text-xs text-gray-500">{r.description}</p>
            <div className="flex gap-1 mt-1">
              <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 px-1.5 py-0.5 rounded">{r.category}</span>
              {r.tags.slice(0, 3).map((t) => (
                <span key={t} className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{t}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
