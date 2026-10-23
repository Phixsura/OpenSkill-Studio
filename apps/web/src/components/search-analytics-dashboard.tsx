"use client";

interface TopQuery { query: string; count: number; }
interface SearchAnalyticsDashboardProps { totalSearches: number; uniqueQueries: number;
  topQueries: TopQuery[]; zeroResultQueries: string[]; zeroResultRate: number; clickThroughRate: number; }

export function SearchAnalyticsDashboard({ totalSearches, uniqueQueries, topQueries, zeroResultQueries, zeroResultRate, clickThroughRate }: SearchAnalyticsDashboardProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Search Analytics</h2>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-xl font-bold">{totalSearches.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Searches</p>
        </div>
        <div className="rounded-lg bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-xl font-bold">{clickThroughRate}%</p>
          <p className="text-xs text-gray-400">CTR</p>
        </div>
        <div className="rounded-lg bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className={`text-xl font-bold ${zeroResultRate > 20 ? "text-red-600" : "text-green-600"}`}>{zeroResultRate}%</p>
          <p className="text-xs text-gray-400">Zero Results</p>
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <h3 className="text-sm font-medium">Top Queries</h3>
          <div className="mt-2 space-y-1">
            {topQueries.map((q, i) => (
              <div key={q.query} className="flex justify-between text-sm">
                <span>{i + 1}. {q.query}</span>
                <span className="text-gray-400">{q.count}</span>
              </div>
            ))}
          </div>
        </div>
        {zeroResultQueries.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-red-600">Zero Result Queries</h3>
            <ul className="mt-2 space-y-1">
              {zeroResultQueries.map(q => (
                <li key={q} className="text-sm text-gray-500">• {q}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
