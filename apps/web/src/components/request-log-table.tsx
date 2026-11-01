"use client";

interface RequestLog { method: string; path: string; statusCode: number; durationMs: number; success: boolean; timestamp: string; }
interface RequestLogTableProps { logs: RequestLog[]; avgDurationMs: number; errorRate: number; }

const methodColors: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600",
  DELETE: "text-red-600", PATCH: "text-orange-600",
};

export function RequestLogTable({ logs, avgDurationMs, errorRate }: RequestLogTableProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Request Log</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>avg {avgDurationMs}ms</span>
          <span className={errorRate > 5 ? "text-red-600" : ""}>{errorRate}% errors</span>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="border-b dark:border-gray-700 text-xs text-gray-400">
            <th className="px-3 py-2 text-left">Method</th><th className="px-3 py-2 text-left">Path</th>
            <th className="px-3 py-2 text-right">Status</th><th className="px-3 py-2 text-right">Duration</th>
          </tr></thead>
          <tbody>
            {logs.slice(0, 20).map((l, i) => (
              <tr key={i} className="border-b dark:border-gray-800">
                <td className={`px-3 py-1.5 font-mono text-xs font-medium ${methodColors[l.method] ?? ""}`}>{l.method}</td>
                <td className="px-3 py-1.5 font-mono text-xs truncate max-w-[200px]">{l.path}</td>
                <td className={`px-3 py-1.5 text-right text-xs ${l.success ? "" : "text-red-600 font-medium"}`}>{l.statusCode}</td>
                <td className="px-3 py-1.5 text-right text-xs text-gray-400">{l.durationMs}ms</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
