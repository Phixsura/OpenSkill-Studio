"use client";

interface SlowQuery { query: string; durationMs: number; table: string; }
interface Suggestion { query: string; suggestion: string; impact: string; }
interface QueryProfilerTableProps { totalQueries: number; slowQueries: number;
  avgTimeMs: number; topSlow: SlowQuery[]; suggestions: Suggestion[]; }

export function QueryProfilerTable({ totalQueries, slowQueries, avgTimeMs, topSlow, suggestions }: QueryProfilerTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Query Profiler</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>{totalQueries} queries</span>
          <span className="text-yellow-600">{slowQueries} slow</span>
          <span>Avg: {avgTimeMs}ms</span>
        </div>
      </div>
      <div className="p-4">
        <h4 className="text-xs font-semibold text-gray-400 mb-2">Slowest Queries</h4>
        <div className="space-y-2 mb-4">
          {topSlow.map((q, i) => (
            <div key={i} className="bg-gray-50 dark:bg-gray-800 rounded px-3 py-2">
              <div className="flex justify-between mb-1">
                <span className="text-xs text-gray-400">{q.table}</span>
                <span className="text-xs font-bold text-red-500">{q.durationMs}ms</span>
              </div>
              <code className="text-xs break-all">{q.query}</code>
            </div>
          ))}
        </div>
        {suggestions.length > 0 && (
          <>
            <h4 className="text-xs font-semibold text-gray-400 mb-2">Suggestions</h4>
            {suggestions.map((s, i) => (
              <div key={i} className="flex items-center gap-2 text-xs py-1">
                <span className="text-yellow-500">💡</span>
                <span className="font-medium">{s.suggestion}</span>
                <span className="text-gray-400">— {s.query.slice(0, 40)}...</span>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}
