"use client";

interface EndpointUsage { endpoint: string; count: number; avg_latency_ms: number; error_count: number; }
interface ApiUsageReportViewProps { period: string; totalCalls: number; successRate: number;
  avgLatencyMs: number; endpoints: EndpointUsage[]; }

export function ApiUsageReportView({ period, totalCalls, successRate, avgLatencyMs, endpoints }: ApiUsageReportViewProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">API Usage Report</h2>
        <span className="text-xs text-gray-400">{period}</span>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-xl font-bold">{totalCalls.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Total Calls</p>
        </div>
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className={`text-xl font-bold ${successRate >= 99 ? "text-green-600" : "text-yellow-600"}`}>{successRate}%</p>
          <p className="text-xs text-gray-400">Success Rate</p>
        </div>
        <div className="rounded bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-xl font-bold">{avgLatencyMs}ms</p>
          <p className="text-xs text-gray-400">Avg Latency</p>
        </div>
      </div>
      <div className="space-y-1.5">
        {endpoints.map(ep => (
          <div key={ep.endpoint} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
            <span className="font-mono text-sm">{ep.endpoint}</span>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>{ep.count.toLocaleString()} calls</span>
              <span>{ep.avg_latency_ms}ms</span>
              {ep.error_count > 0 && <span className="text-red-500">{ep.error_count} errors</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
