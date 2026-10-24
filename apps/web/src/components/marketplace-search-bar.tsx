"use client";

import { useState } from "react";

interface MarketplaceSearchBarProps { recentSearches: string[]; popularSearches: string[];
  onSearch: (query: string) => void; }

export function MarketplaceSearchBar({ recentSearches, popularSearches, onSearch }: MarketplaceSearchBarProps) {
  const [query, setQuery] = useState("");
  const [focused, setFocused] = useState(false);

  return (
    <div className="relative w-full max-w-xl mx-auto">
      <div className="flex gap-2">
        <input value={query} onChange={e => setQuery(e.target.value)}
          onFocus={() => setFocused(true)} onBlur={() => setTimeout(() => setFocused(false), 200)}
          onKeyDown={e => e.key === "Enter" && onSearch(query)}
          placeholder="🔍 Search apps, integrations, tools..."
          className="flex-1 rounded-xl border px-4 py-3 text-sm dark:bg-gray-800 dark:border-gray-600" />
        <button onClick={() => onSearch(query)}
          className="rounded-xl bg-blue-600 px-5 py-3 text-sm text-white font-medium">Search</button>
      </div>
      {focused && !query && (
        <div className="absolute left-0 right-0 z-10 mt-2 rounded-xl border bg-white p-3 shadow-xl dark:bg-gray-900 dark:border-gray-700">
          {recentSearches.length > 0 && (
            <div className="mb-2">
              <p className="text-xs font-semibold text-gray-400 mb-1">Recent</p>
              <div className="flex flex-wrap gap-1">{recentSearches.map(s => (
                <button key={s} onClick={() => { setQuery(s); onSearch(s); }}
                  className="rounded-full bg-gray-100 px-2.5 py-1 text-xs dark:bg-gray-800">{s}</button>
              ))}</div>
            </div>
          )}
          <div>
            <p className="text-xs font-semibold text-gray-400 mb-1">Popular</p>
            <div className="flex flex-wrap gap-1">{popularSearches.map(s => (
              <button key={s} onClick={() => { setQuery(s); onSearch(s); }}
                className="rounded-full bg-blue-50 px-2.5 py-1 text-xs text-blue-700 dark:bg-blue-900/20 dark:text-blue-300">{s}</button>
            ))}</div>
          </div>
        </div>
      )}
    </div>
  );
}
