"use client";

interface SearchResult { id: string; name: string; icon: string; description: string; }
interface SearchResultsPageProps { results: SearchResult[]; query: string;
  total: number; onSelect: (id: string) => void; }

export function SearchResultsPage({ results, query, total, onSelect }: SearchResultsPageProps) {
  return (
    <div>
      <p className="text-sm text-gray-400 mb-4">{total} results for &ldquo;{query}&rdquo;</p>
      <div className="space-y-2">
        {results.map(r => (
          <button key={r.id} onClick={() => onSelect(r.id)}
            className="w-full text-left flex items-center gap-3 rounded-xl border dark:border-gray-700 p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition">
            <span className="text-2xl">{r.icon}</span>
            <div>
              <p className="text-sm font-bold">{r.name}</p>
              <p className="text-xs text-gray-500">{r.description}</p>
            </div>
          </button>
        ))}
        {results.length === 0 && <p className="text-sm text-gray-400 text-center py-8">No results found</p>}
      </div>
    </div>
  );
}
