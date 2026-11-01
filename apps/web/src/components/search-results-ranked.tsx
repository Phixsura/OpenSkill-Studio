"use client";

interface RankedApp { name: string; description?: string; installs: number;
  rating: number; score: number; }
interface SearchResultsRankedProps { results: RankedApp[]; query: string; }

export function SearchResultsRanked({ results, query }: SearchResultsRankedProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Results for &ldquo;{query}&rdquo;</h3>
        <p className="text-xs text-gray-400">{results.length} apps found</p>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map((app, i) => (
          <div key={app.name} className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-3">
              <span className="text-lg font-bold text-gray-300 w-6">{i + 1}</span>
              <div>
                <p className="text-sm font-medium">{app.name}</p>
                {app.description && <p className="text-xs text-gray-400">{app.description}</p>}
                <div className="flex gap-2 mt-0.5 text-xs text-gray-400">
                  <span>⭐ {app.rating}</span>
                  <span>📥 {app.installs.toLocaleString()}</span>
                </div>
              </div>
            </div>
            <span className="text-xs font-mono text-gray-300">{app.score}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
