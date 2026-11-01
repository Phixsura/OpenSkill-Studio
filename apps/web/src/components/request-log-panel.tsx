"use client";

interface LogEntry { method: string; path: string; statusCode: number; latencyMs: number; }
interface LogStats { total: number; avgLatency: number; errorCount: number; }

const mc: Record<string, string> = { GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600" };

export function RequestLogPanel({ entries, stats }: { entries: LogEntry[]; stats: LogStats }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📋 Request Log</h2>
        <span className="text-sm text-gray-500">{stats.total} reqs · {stats.avgLatency}ms avg · {stats.errorCount} errors</span>
      </div>
      <div className="space-y-0.5">
        {entries.map((e, i) => (
          <div key={i} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span className={`font-bold text-xs w-12 ${mc[e.method] || ""}`}>{e.method}</span>
              <code className="text-xs">{e.path}</code>
            </div>
            <div className="flex gap-2 text-xs">
              <span className={e.statusCode >= 400 ? "text-red-600 font-bold" : "text-green-600"}>{e.statusCode}</span>
              <span className="text-gray-400">{e.latencyMs}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
