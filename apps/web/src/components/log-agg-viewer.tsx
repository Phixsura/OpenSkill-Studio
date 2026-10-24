"use client";

interface LogSource { source: string; count: number; }
interface LogAggViewerProps { total: number; byLevel: Record<string, number>;
  topSources: LogSource[]; hasErrors: boolean; errorCount: number; }

export function LogAggViewer({ total, byLevel, topSources, hasErrors, errorCount }: LogAggViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Log Aggregation</h3>
        <span className={`text-xs ${hasErrors ? "text-red-500" : "text-green-600"}`}>
          {total.toLocaleString()} logs · {errorCount} errors
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4">
        {Object.entries(byLevel).map(([level, count]) => (
          <div key={level} className="text-xs">
            <span className={`uppercase font-bold ${level === "error" || level === "fatal" ? "text-red-500" : "text-gray-500"}`}>{level}</span>
            <span className="ml-2 text-gray-400">{count}</span>
          </div>
        ))}
      </div>
      {topSources.length > 0 && (
        <div className="border-t dark:border-gray-700 p-4">
          <div className="text-xs text-gray-400 mb-1">Top Sources</div>
          {topSources.map(s => (
            <div key={s.source} className="flex justify-between text-xs font-mono">
              <span>{s.source}</span><span className="text-gray-400">{s.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
