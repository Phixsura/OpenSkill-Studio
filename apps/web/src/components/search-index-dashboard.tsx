"use client";

interface SearchResult { id: string; score: number; matchedTerms: string[]; }
interface SearchIndexDashboardProps { totalDocuments: number; totalWords: number;
  results: SearchResult[]; query: string; onSearch: (q: string) => void; }

export function SearchIndexDashboard({ totalDocuments, totalWords, results, query, onSearch }: SearchIndexDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔎 Search Index</h3>
        <span className="text-xs text-gray-400">{totalDocuments} docs · {totalWords} words</span>
      </div>
      <div className="p-3 border-b dark:border-gray-700">
        <input defaultValue={query} onKeyDown={e => e.key === "Enter" && onSearch((e.target as HTMLInputElement).value)}
          placeholder="Search..." className="w-full px-3 py-1.5 text-sm border rounded-lg dark:bg-gray-800 dark:border-gray-600" />
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.id} className="flex items-center justify-between px-4 py-2">
            <div className="flex items-center gap-2">
              <span className="text-sm font-mono">{r.id}</span>
              <div className="flex gap-1">
                {r.matchedTerms.map(t => (
                  <span key={t} className="px-1 py-0.5 text-[10px] bg-yellow-100 dark:bg-yellow-900/20 rounded">{t}</span>
                ))}
              </div>
            </div>
            <span className="text-xs text-gray-400">score: {r.score}</span>
          </div>
        ))}
        {results.length === 0 && query && <div className="p-4 text-center text-sm text-gray-400">No results</div>}
      </div>
    </div>
  );
}
