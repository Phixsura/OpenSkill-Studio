"use client";

import { useState } from "react";

interface SearchResult { id: string; name: string; category?: string; rating?: number; }
interface Facets { categories: Record<string, number>; }
interface MarketplaceSearchPageProps { results: SearchResult[]; total: number; query: string;
  facets: Facets; page: number; totalPages: number;
  onSearch: (query: string) => void; onFilter: (category: string) => void;
  onAppClick: (id: string) => void; onPage: (page: number) => void; }

export function MarketplaceSearchPage({ results, total, query, facets, page, totalPages,
  onSearch, onFilter, onAppClick, onPage }: MarketplaceSearchPageProps) {
  const [q, setQ] = useState(query);
  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input value={q} onChange={e => setQ(e.target.value)} placeholder="Search apps..."
          className="flex-1 rounded-lg border px-4 py-2.5 text-sm dark:border-gray-600 dark:bg-gray-700"
          onKeyDown={e => e.key === "Enter" && onSearch(q)} />
        <button onClick={() => onSearch(q)} className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm text-white">Search</button>
      </div>
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-400">{total} results for &quot;{query}&quot;</p>
        <div className="flex gap-1">
          {Object.entries(facets.categories).slice(0, 5).map(([cat, count]) => (
            <button key={cat} onClick={() => onFilter(cat)}
              className="rounded-full border px-2.5 py-0.5 text-xs dark:border-gray-600">
              {cat} ({count})
            </button>
          ))}
        </div>
      </div>
      <div className="space-y-2">
        {results.map(r => (
          <button key={r.id} onClick={() => onAppClick(r.id)}
            className="flex w-full items-center justify-between rounded-lg border p-3 text-left hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
            <div>
              <p className="font-medium">{r.name}</p>
              {r.category && <span className="text-xs text-gray-400">{r.category}</span>}
            </div>
            {r.rating && <span className="text-xs text-yellow-500">⭐ {r.rating}</span>}
          </button>
        ))}
      </div>
      {totalPages > 1 && (
        <div className="flex justify-center gap-1">
          {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => i + 1).map(p => (
            <button key={p} onClick={() => onPage(p)}
              className={`rounded px-2.5 py-1 text-xs ${p === page ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>{p}</button>
          ))}
        </div>
      )}
    </div>
  );
}
