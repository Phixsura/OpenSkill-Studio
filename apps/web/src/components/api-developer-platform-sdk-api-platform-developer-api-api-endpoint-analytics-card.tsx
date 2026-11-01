"use client";

interface EndpointInfo { endpoint: string; method: string; total_requests: number; error_rate: number; avg_latency: number; top_consumer: string; }
interface Props { endpoints: EndpointInfo[]; highErrorCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointAnalyticsCard({ endpoints, highErrorCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Endpoint Analytics</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {endpoints.length} endpoints</p>
        </div>
        {highErrorCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">⚠️ {highErrorCount} high-error</span>}
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No analytics data</p>
      ) : (
        <div className="space-y-1.5">
          {endpoints.map((e) => (
            <div key={`${e.method}-${e.endpoint}`} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{e.method} {e.endpoint}</span>
                <span className="text-gray-400">{e.total_requests.toLocaleString()} reqs</span>
              </div>
              <div className="flex gap-3 text-[10px] text-gray-400">
                <span className={e.error_rate > 5 ? "text-red-500" : ""}>err: {e.error_rate}%</span>
                <span>avg: {e.avg_latency}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
