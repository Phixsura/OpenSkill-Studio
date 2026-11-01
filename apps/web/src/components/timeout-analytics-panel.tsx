"use client";
interface TimeoutEp { endpoint: string; timeouts: number; total: number; timeoutRate: number; }
interface TimeoutAnalyticsPanelProps { endpoints: TimeoutEp[]; totalTimeouts: number;
  totalRequests: number; thresholdMs: number; overallRate: number; }
export function TimeoutAnalyticsPanel({ endpoints, totalTimeouts, totalRequests, thresholdMs, overallRate }: TimeoutAnalyticsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏰ Timeout Analytics</h3>
        <span className={`text-xs ${totalTimeouts > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {totalTimeouts} timeouts ({overallRate}%) · {thresholdMs}ms threshold
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(e => (
          <div key={e.endpoint} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{e.endpoint}</span>
            <span className="text-yellow-600">{e.timeouts} timeouts ({e.timeoutRate}%)</span>
          </div>
        ))}
        {endpoints.length === 0 && <div className="p-4 text-xs text-green-600 text-center">No timeouts</div>}
      </div>
    </div>
  );
}
