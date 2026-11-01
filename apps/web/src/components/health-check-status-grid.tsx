"use client";

interface Check { url: string; status_code: number; latency_ms: number; healthy: boolean; }
interface HealthCheckStatusGridProps { checks: Check[]; allHealthy: boolean; avgLatencyMs: number; }

export function HealthCheckStatusGrid({ checks, allHealthy, avgLatencyMs }: HealthCheckStatusGridProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Health Checks</h2>
        <div className="flex items-center gap-2">
          <span className={`h-2.5 w-2.5 rounded-full ${allHealthy ? "bg-green-500" : "bg-red-500"}`} />
          <span className="text-sm text-gray-400">{avgLatencyMs}ms avg</span>
        </div>
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        {checks.map(c => (
          <div key={c.url} className={`rounded-lg border p-3 ${c.healthy ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
            <div className="flex items-center justify-between">
              <span className="font-mono text-sm">{c.url}</span>
              <span className={`text-xs font-bold ${c.healthy ? "text-green-600" : "text-red-600"}`}>{c.status_code}</span>
            </div>
            <p className="mt-1 text-xs text-gray-400">{c.latency_ms}ms</p>
          </div>
        ))}
      </div>
    </div>
  );
}
