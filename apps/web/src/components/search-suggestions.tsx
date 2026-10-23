"use client";

interface SearchSuggestionsProps { suggestions: string[]; trending: { query: string; trend: string }[];
  showTrending: boolean; onSelect: (query: string) => void; }

export function SearchSuggestions({ suggestions, trending, showTrending, onSelect }: SearchSuggestionsProps) {
  const items = showTrending ? trending : suggestions.map(s => ({ query: s, trend: "" }));
  if (!items.length) return null;
  return (
    <div className="rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 shadow-xl py-1">
      {showTrending && <p className="px-3 py-1 text-xs text-gray-400">🔥 Trending</p>}
      {items.map(item => (
        <button key={item.query} onClick={() => onSelect(item.query)}
          className="w-full text-left px-3 py-1.5 text-sm hover:bg-gray-50 dark:hover:bg-gray-800">
          {item.trend} {item.query}
        </button>
      ))}
    </div>
  );
}
