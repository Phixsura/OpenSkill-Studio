"use client";

import { useState } from "react";

interface SearchResult {
  id: string;
  type: "extension" | "connector" | "developer" | "doc";
  title: string;
  description: string;
  icon: string;
  meta: string;
}

export function MarketplaceGlobalSearch({
  onSearch,
  results,
  onSelect,
}: {
  onSearch?: (query: string) => void;
  results: SearchResult[];
  onSelect?: (id: string, type: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [focused, setFocused] = useState(false);

  const handleSearch = (value: string) => {
    setQuery(value);
    onSearch?.(value);
  };

  const typeIcons: Record<string, string> = {
    extension: "📦", connector: "🔌", developer: "👩‍💻", doc: "📄",
  };

  const typeColors: Record<string, string> = {
    extension: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
    connector: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
    developer: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300",
    doc: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300",
  };

  const showResults = focused && query.length > 0 && results.length > 0;

  return (
    <div className="relative max-w-xl mx-auto">
      <div className="relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
        <input
          type="text"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setTimeout(() => setFocused(false), 200)}
          placeholder="Search extensions, connectors, developers..."
          className="w-full rounded-xl border dark:border-gray-700 bg-white dark:bg-gray-900 pl-10 pr-4 py-3 text-sm"
        />
        {query && (
          <button
            onClick={() => handleSearch("")}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        )}
      </div>

      {showResults && (
        <div className="absolute top-full left-0 right-0 mt-1 rounded-xl border dark:border-gray-700 bg-white dark:bg-gray-900 shadow-lg z-50 max-h-80 overflow-y-auto">
          {results.map((r) => (
            <button
              key={r.id}
              onClick={() => onSelect?.(r.id, r.type)}
              className="w-full text-left flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800 border-b dark:border-gray-800 last:border-0"
            >
              <span className="text-xl">{r.icon || typeIcons[r.type]}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm truncate">{r.title}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded ${typeColors[r.type]}`}>{r.type}</span>
                </div>
                <p className="text-xs text-gray-400 truncate">{r.description}</p>
              </div>
              <span className="text-xs text-gray-400 shrink-0">{r.meta}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
