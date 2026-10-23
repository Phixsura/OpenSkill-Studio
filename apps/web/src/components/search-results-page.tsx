"use client";

interface SearchResult { id: string; name: string; icon: string; tagline: string;
  category: string; rating: number; downloads: number; verified: boolean; }
interface SearchResultsPageProps { query: string; results: SearchResult[]; total: number;
  sortBy: string; categories: Record<string, number>; hasResults: boolean;
  onSort: (sort: string) => void; onFilterCategory: (cat: string | null) => void;
  onSelect: (id: string) => void; }

export function SearchResultsPage({ query, results, total, sortBy, categories,
  hasResults, onSort, onFilterCategory, onSelect }: SearchResultsPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔍 Results for &ldquo;{query}&rdquo;</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{total} results</span>
          <select value={sortBy} onChange={e => onSort(e.target.value)}
            className="rounded border px-2 py-1 text-xs dark:bg-gray-800 dark:border-gray-600">
            <option value="relevance">Relevance</option>
            <option value="downloads">Downloads</option>
            <option value="rating">Rating</option>
          </select>
        </div>
      </div>
      <div className="flex gap-1">
        <button onClick={() => onFilterCategory(null)} className="rounded px-2 py-0.5 text-xs bg-blue-600 text-white">All</button>
        {Object.entries(categories).map(([cat, count]) => (
          <button key={cat} onClick={() => onFilterCategory(cat)}
            className="rounded px-2 py-0.5 text-xs bg-gray-100 dark:bg-gray-800 capitalize">{cat} ({count})</button>
        ))}
      </div>
      {hasResults ? (
        <div className="space-y-2">
          {results.map(r => (
            <button key={r.id} onClick={() => onSelect(r.id)}
              className="flex w-full items-center gap-3 rounded-xl border p-3 text-left hover:shadow dark:border-gray-700">
              <span className="text-2xl">{r.icon}</span>
              <div className="flex-1">
                <div className="flex items-center gap-1.5">
                  <span className="text-sm font-semibold">{r.name}</span>
                  {r.verified && <span className="text-blue-500 text-xs">✓</span>}
                </div>
                <p className="text-xs text-gray-400">{r.tagline}</p>
                <div className="mt-1 flex gap-2 text-xs text-gray-400">
                  <span>⭐ {r.rating}</span>
                  <span>{r.downloads.toLocaleString()} downloads</span>
                </div>
              </div>
            </button>
          ))}
        </div>
      ) : (
        <div className="py-12 text-center">
          <span className="text-4xl">🔍</span>
          <p className="mt-2 text-gray-500">No results for &ldquo;{query}&rdquo;</p>
        </div>
      )}
    </div>
  );
}
