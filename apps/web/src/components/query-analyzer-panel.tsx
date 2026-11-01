"use client";

interface QueryResult { queryPreview: string; executionMs: number; rowsScanned: number;
  rowsReturned: number; indexUsed: boolean; efficiencyPct: number; slow: boolean;
  suggestions: string[]; }
interface QueryAnalyzerPanelProps { queries: QueryResult[]; }

export function QueryAnalyzerPanel({ queries }: QueryAnalyzerPanelProps) {
  const slowCount = queries.filter(q => q.slow).length;
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔎 Query Analyzer</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{queries.length} queries</span>
          {slowCount > 0 && <span className="text-red-500">{slowCount} slow</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {queries.map((q, i) => (
          <div key={i} className="px-4 py-2.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono truncate max-w-[250px]">{q.queryPreview}</span>
              <span className={`text-xs font-mono ${q.slow ? "text-red-500 font-bold" : ""}`}>{q.executionMs}ms</span>
            </div>
            <div className="flex gap-3 text-[10px] text-gray-400 mt-0.5">
              <span>{q.rowsReturned}/{q.rowsScanned} rows ({q.efficiencyPct}%)</span>
              <span>{q.indexUsed ? "✅ indexed" : "⚠ no index"}</span>
            </div>
            {q.suggestions.length > 0 && (
              <div className="mt-1">{q.suggestions.map((s, j) => (
                <div key={j} className="text-[10px] text-yellow-600">💡 {s}</div>
              ))}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
