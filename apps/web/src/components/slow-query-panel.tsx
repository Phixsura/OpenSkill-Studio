"use client";
interface SlowQuery { query: string; durationMs: number; table: string; }
interface SlowQueryPanelProps { queries: SlowQuery[]; thresholdMs: number; total: number; }
export function SlowQueryPanel({ queries, thresholdMs, total }: SlowQueryPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🐌 Slow Queries</h3>
        <span className={`text-xs ${total > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {total} slow (>{thresholdMs}ms)
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {queries.map((q, i) => (
          <div key={i} className="px-4 py-1.5 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="text-gray-400">{q.table}</span>
              <span className="text-red-500 font-bold">{q.durationMs}ms</span>
            </div>
            <div className="font-mono text-gray-500 truncate">{q.query}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
