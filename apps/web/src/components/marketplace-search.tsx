"use client";

import { useState } from "react";

interface SearchResult { name: string; description: string; icon?: string; category: string;
  downloads: number; rating: number; }
interface MarketplaceSearchProps { results: SearchResult[]; total: number; query: string;
  facets: Record<string, Record<string, number>>; sortOptions: string[];
  onSearch: (query: string) => void; onSort: (sort: string) => void; }

export function MarketplaceSearch({ results, total, query, facets, sortOptions, onSearch, onSort }: MarketplaceSearchProps) {
  const [input, setInput] = useState(query);
  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && onSearch(input)}
          placeholder="Search apps..."
          className="flex-1 rounded-lg border px-4 py-2.5 text-sm dark:bg-gray-800 dark:border-gray-600" />
        <button onClick={() => onSearch(input)} className="rounded-lg bg-blue-600 px-4 py-2.5 text-sm text-white">Search</button>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-400">{total} results</span>
        <select onChange={e => onSort(e.target.value)} className="rounded border px-2 py-1 text-xs dark:bg-gray-800 dark:border-gray-600">
          {sortOptions.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>
      <div className="space-y-2">
        {results.map((r, i) => (
          <div key={i} className="rounded-lg border p-3 hover:shadow dark:border-gray-700">
            <h4 className="text-sm font-semibold">{r.name}</h4>
            <p className="text-xs text-gray-500 mt-0.5">{r.description}</p>
            <div className="mt-2 flex gap-3 text-xs text-gray-400">
              <span>⭐ {r.rating}</span>
              <span>📥 {r.downloads.toLocaleString()}</span>
              <span className="capitalize">{r.category}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
