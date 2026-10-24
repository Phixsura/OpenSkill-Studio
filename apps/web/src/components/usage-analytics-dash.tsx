"use client";

interface EndpointUsage { endpoint: string; count: number; avgMs: number; errorRate: number; }
interface UsageAnalyticsDashProps { endpoints: EndpointUsage[]; totalRequests: number; uniqueEndpoints: number; }

export function UsageAnalyticsDash({ endpoints, totalRequests, uniqueEndpoints }: UsageAnalyticsDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 API Usage</h3>
        <span className="text-xs text-gray-400">{totalRequests.toLocaleString()} reqs · {uniqueEndpoints} endpoints</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {endpoints.map(e => (
          <div key={e.endpoint} className="flex items-center justify-between px-4 py-2 text-xs">
            <span className="font-mono">{e.endpoint}</span>
            <div className="flex items-center gap-3 text-gray-400">
              <span>{e.count.toLocaleString()} calls</span>
              <span>{e.avgMs}ms</span>
              <span className={e.errorRate > 5 ? "text-red-500" : ""}>{e.errorRate}% err</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
