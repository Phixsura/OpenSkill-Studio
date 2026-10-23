"use client";

interface EndpointStats { url: string; uptime_pct: number; avg_latency_ms: number; }
interface EndpointMonitorViewProps { endpoints: EndpointStats[]; overallUptime: number;
  avgLatencyMs: number; totalChecks: number; periodHours: number; onRefresh: () => void; }

export function EndpointMonitorView({ endpoints, overallUptime, avgLatencyMs, totalChecks,
  periodHours, onRefresh }: EndpointMonitorViewProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Endpoint Monitor</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">Last {periodHours}h · {totalChecks} checks</span>
          <button onClick={onRefresh} className="rounded bg-blue-600 px-3 py-1 text-xs text-white">Refresh</button>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-lg bg-green-50 p-4 text-center dark:bg-green-900/10">
          <p className={`text-2xl font-bold ${overallUptime >= 99.9 ? "text-green-600" : "text-yellow-600"}`}>{overallUptime}%</p>
          <p className="text-xs text-gray-400">Overall Uptime</p>
        </div>
        <div className="rounded-lg bg-blue-50 p-4 text-center dark:bg-blue-900/10">
          <p className="text-2xl font-bold">{avgLatencyMs}ms</p>
          <p className="text-xs text-gray-400">Avg Latency</p>
        </div>
      </div>
      <div className="space-y-2">
        {endpoints.map(ep => (
          <div key={ep.url} className={`flex items-center justify-between rounded-lg border p-3 ${ep.uptime_pct >= 99 ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
            <div className="flex items-center gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${ep.uptime_pct >= 99 ? "bg-green-500" : "bg-red-500"}`} />
              <span className="font-mono text-sm">{ep.url}</span>
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>{ep.uptime_pct}%</span>
              <span>{ep.avg_latency_ms}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
