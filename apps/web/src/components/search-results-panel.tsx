"use client";

interface SearchResult { id: string; title: string; score: number; type: string; }
interface SearchResultsPanelProps { query: string; results: SearchResult[]; totalDocs: number; }

export function SearchResultsPanel({ query, results, totalDocs }: SearchResultsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Search Results</h3>
        <span className="text-xs text-gray-400">{results.length} results · {totalDocs} indexed</span>
      </div>
      {results.length > 0 ? (
        <div className="divide-y dark:divide-gray-700">
          {results.map(r => (
            <div key={r.id} className="flex items-center justify-between px-4 py-2 text-xs">
              <div>
                <span className="font-semibold">{r.title}</span>
                <span className="ml-2 px-1 rounded bg-gray-100 dark:bg-gray-800 text-[10px]">{r.type}</span>
              </div>
              <span className="text-gray-400">{(r.score * 100).toFixed(0)}% match</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-xs text-gray-400 text-center">No results for "{query}"</div>
      )}
    </div>
  );
}
