"use client";

interface EndpointLatency { endpoint: string; count: number; avgMs: number;
  p50Ms: number; p99Ms: number; status: string; }
interface ResponseTimeMonitorProps { endpoints: EndpointLatency[];
  overallAvgMs: number; totalSamples: number; slowest: string | null; }

const STATUS_DOT: Record<string, string> = { fast: "bg-green-500", ok: "bg-yellow-500", slow: "bg-red-500" };

export function ResponseTimeMonitor({ endpoints, overallAvgMs, totalSamples, slowest }: ResponseTimeMonitorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏱️ Response Times</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>Avg: {overallAvgMs}ms</span>
          <span>{totalSamples} samples</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(e => (
          <div key={e.endpoint} className={`flex items-center justify-between px-4 py-2 ${e.endpoint === slowest ? "bg-red-50/50 dark:bg-red-900/5" : ""}`}>
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${STATUS_DOT[e.status] || ""}`} />
              <span className="text-sm font-mono">{e.endpoint}</span>
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>avg {e.avgMs}ms</span>
              <span>p50 {e.p50Ms}ms</span>
              <span>p99 {e.p99Ms}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
