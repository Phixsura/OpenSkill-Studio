"use client";

interface RequestLog { request_id: string; method: string; path: string; status_code: number;
  latency_ms: number; level: string; timestamp: string; }
interface RequestLogViewerProps { logs: RequestLog[]; totalRequests: number;
  avgLatencyMs: number; errorRate: number; }

const statusColor = (s: number) => s < 300 ? "text-green-600" : s < 400 ? "text-blue-600" : s < 500 ? "text-yellow-600" : "text-red-600";
const methodBg: Record<string, string> = {
  GET: "bg-green-100 dark:bg-green-900/30", POST: "bg-blue-100 dark:bg-blue-900/30",
  PUT: "bg-yellow-100 dark:bg-yellow-900/30", DELETE: "bg-red-100 dark:bg-red-900/30",
};

export function RequestLogViewer({ logs, totalRequests, avgLatencyMs, errorRate }: RequestLogViewerProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Request Log</h2>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>{totalRequests} req</span>
          <span>{avgLatencyMs}ms avg</span>
          <span className={errorRate > 1 ? "text-red-500" : "text-green-500"}>{errorRate}% errors</span>
        </div>
      </div>
      <div className="max-h-60 overflow-y-auto rounded border bg-gray-900 p-2 dark:border-gray-700">
        {logs.map(l => (
          <div key={l.request_id} className="flex items-center gap-2 py-0.5 font-mono text-xs">
            <span className="w-14 text-gray-500">{l.timestamp.slice(11, 19)}</span>
            <span className={`w-10 rounded px-1 text-center text-[10px] font-bold ${methodBg[l.method] ?? ""}`}>{l.method}</span>
            <span className={`w-8 font-bold ${statusColor(l.status_code)}`}>{l.status_code}</span>
            <span className="flex-1 text-gray-300">{l.path}</span>
            <span className="w-12 text-right text-gray-500">{l.latency_ms}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
