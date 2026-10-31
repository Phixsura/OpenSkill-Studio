"use client";

interface LogEntry { id: string; method: string; path: string; status: number;
  durationMs: number; userId: string; error: boolean; }
interface RequestLogViewerProps { entries: LogEntry[]; total: number;
  errorRate: number; avgDurationMs: number; }

const METHOD_COLOR: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600",
  DELETE: "text-red-600", PATCH: "text-orange-600",
};

export function RequestLogViewer({ entries, total, errorRate, avgDurationMs }: RequestLogViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Request Log</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>{total} requests</span>
          <span className="text-red-500">{errorRate}% errors</span>
          <span>Avg {avgDurationMs}ms</span>
        </div>
      </div>
      <div className="max-h-64 overflow-y-auto font-mono text-xs">
        {entries.map(e => (
          <div key={e.id} className={`flex items-center gap-2 px-4 py-1.5 border-b last:border-0 dark:border-gray-800 ${e.error ? "bg-red-50/50 dark:bg-red-900/5" : ""}`}>
            <span className={`font-bold w-10 ${METHOD_COLOR[e.method] || ""}`}>{e.method}</span>
            <span className={`w-8 ${e.status >= 400 ? "text-red-500" : "text-green-600"}`}>{e.status}</span>
            <span className="flex-1 truncate">{e.path}</span>
            <span className="text-gray-400 w-12 text-right">{e.durationMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
