"use client";
import { useState } from "react";

interface SearchResult { extensionId: string; name: string; description: string; installs: number; rating: number; tags: string[]; }

export function MarketplaceSearchBar({ results, suggestions, onSearch, onSelect }: {
  results: SearchResult[]; suggestions?: string[]; onSearch?: (q: string) => void; onSelect?: (id: string) => void;
}) {
  const [query, setQuery] = useState("");
  const handleSearch = () => onSearch?.(query);

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <input type="text" value={query} onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSearch()}
          placeholder="Search extensions..." className="flex-1 border dark:border-gray-700 rounded-lg px-3 py-2 text-sm bg-transparent" />
        <button onClick={handleSearch} className="bg-blue-500 text-white px-4 py-2 rounded-lg text-sm">🔍</button>
      </div>
      {suggestions && suggestions.length > 0 && (
        <div className="flex gap-1 flex-wrap">
          {suggestions.map(s => <button key={s} onClick={() => { setQuery(s); onSearch?.(s); }} className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded-full">{s}</button>)}
        </div>
      )}
      <div className="space-y-2">
        {results.map(r => (
          <button key={r.extensionId} onClick={() => onSelect?.(r.extensionId)}
            className="w-full text-left border dark:border-gray-700 rounded-xl p-3 hover:border-blue-400">
            <div className="flex justify-between">
              <span className="font-medium text-sm">{r.name}</span>
              <span className="text-xs text-yellow-500">{"★".repeat(Math.round(r.rating))}</span>
            </div>
            <p className="text-xs text-gray-500 mt-0.5">{r.description}</p>
            <div className="flex gap-1 mt-1">
              {r.tags.map(t => <span key={t} className="text-xs bg-blue-100 dark:bg-blue-900/20 text-blue-600 px-1.5 py-0.5 rounded">{t}</span>)}
              <span className="text-xs text-gray-400 ml-auto">{r.installs} installs</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
