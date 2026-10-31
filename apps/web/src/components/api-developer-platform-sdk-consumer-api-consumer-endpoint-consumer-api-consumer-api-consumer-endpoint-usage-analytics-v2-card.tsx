"use client";

interface Analytics { endpoint: string; totalRequests: number; uniqueConsumers: number; avgMs: number; p95Ms: number; errorRate: number; rpm: number; topConsumers: [string, number][]; }
interface Props { analytics: Analytics[]; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerEndpointUsageAnalyticsV2Card({ analytics, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📈 Endpoint Analytics V2</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {analytics.length} endpoints</p>
      </div>
      {analytics.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No analytics data</p>
      ) : (
        <div className="space-y-2">
          {analytics.slice(0, 5).map((a) => (
            <div key={a.endpoint} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{a.endpoint}</code>
                <span className="text-gray-400">{a.totalRequests.toLocaleString()} req</span>
              </div>
              <div className="mt-0.5 grid grid-cols-4 gap-1 text-center text-[10px] text-gray-400">
                <span>{a.avgMs}ms avg</span>
                <span>{a.p95Ms}ms p95</span>
                <span className={a.errorRate > 1 ? "text-red-500" : ""}>{a.errorRate}% err</span>
                <span>{a.rpm} rpm</span>
              </div>
              {a.uniqueConsumers > 1 && <div className="mt-0.5 text-[9px] text-gray-400">{a.uniqueConsumers} consumers</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
