"use client";

interface SearchResult { id: string; title: string; snippet: string; score: number; tags: string[]; }
interface SearchResultsProps { results: SearchResult[]; query: string; total: number; }

export function SearchResults({ results, query, total }: SearchResultsProps) {
  return (
    <div className="space-y-3">
      <p className="text-xs text-gray-400">{total} result{total !== 1 ? "s" : ""} for &ldquo;{query}&rdquo;</p>
      {results.map(r => (
        <div key={r.id} className="rounded-lg border p-3 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800/50">
          <h4 className="text-sm font-semibold">{r.title}</h4>
          <p className="mt-1 text-xs text-gray-500 line-clamp-2">{r.snippet}</p>
          <div className="mt-2 flex items-center gap-2">
            {r.tags.map(t => (
              <span key={t} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{t}</span>
            ))}
            <span className="ml-auto text-xs text-gray-400">score: {r.score}</span>
          </div>
        </div>
      ))}
      {results.length === 0 && <p className="py-8 text-center text-sm text-gray-400">No results found</p>}
    </div>
  );
}
