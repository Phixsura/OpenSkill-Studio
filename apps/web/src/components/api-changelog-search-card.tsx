"use client";

interface SearchResultInfo {
  entry_id: string;
  title: string;
  version: string;
  score: number;
}

interface APIChangelogSearchCardProps {
  results: SearchResultInfo[];
  query: string;
  totalIndexed: number;
  appName: string;
}

export default function APIChangelogSearchCard({ results, query, totalIndexed, appName }: APIChangelogSearchCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 Changelog Search</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalIndexed} indexed</span>
      </div>

      {query && <p className="mb-2 text-xs text-gray-500">Results for &ldquo;{query}&rdquo;</p>}

      {results.length === 0 ? (
        <p className="text-center text-sm text-gray-400">{query ? "No matches" : "Search changelog"}</p>
      ) : (
        <div className="space-y-1">
          {results.map((r) => (
            <div key={r.entry_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-700 dark:text-gray-300">{r.title}</span>
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{r.version}</span>
              </div>
              <span className="text-[10px] text-gray-400">{r.score}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
