"use client";
import { useState } from "react";

interface SearchResult { title: string; description: string; type: string;
  url: string; icon: string; }
interface GlobalSearchModalProps { results: SearchResult[]; total: number;
  onSearch: (query: string) => void; onSelect: (url: string) => void; }

export function GlobalSearchModal({ results, total, onSearch, onSelect }: GlobalSearchModalProps) {
  const [query, setQuery] = useState("");
  const handleChange = (val: string) => { setQuery(val); onSearch(val); };
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden max-w-lg w-full">
      <div className="p-3 border-b dark:border-gray-700">
        <div className="flex items-center gap-2 bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
          <span className="text-gray-400">🔍</span>
          <input value={query} onChange={e => handleChange(e.target.value)}
            placeholder="Search apps, docs, settings..."
            className="flex-1 bg-transparent text-sm outline-none" autoFocus />
          {query && <span className="text-xs text-gray-400">{total} results</span>}
        </div>
      </div>
      {results.length > 0 && (
        <div className="max-h-72 overflow-y-auto divide-y dark:divide-gray-700">
          {results.map((r, i) => (
            <button key={i} onClick={() => onSelect(r.url)}
              className="w-full flex items-start gap-3 px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-800">
              <span className="text-lg">{r.icon}</span>
              <div>
                <p className="text-sm font-medium">{r.title}</p>
                <p className="text-xs text-gray-400 line-clamp-1">{r.description}</p>
                <span className="text-xs text-gray-300">{r.type}</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
