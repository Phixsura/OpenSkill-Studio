"use client";

interface Analytics { tokenId: string; totalRequests: number; uniqueEndpoints: number; uniqueIps: number; errorCount: number; lastUsed: string | null; topEndpoints: [string, number][]; }
interface Props { analytics: Analytics[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiTokenAnalyticsCard({ analytics, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Token Analytics</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {analytics.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No token usage data</p>
      ) : (
        <div className="space-y-2">
          {analytics.map((a) => (
            <div key={a.tokenId} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{a.tokenId}</code>
                <span className="text-gray-400">{a.totalRequests.toLocaleString()} req</span>
              </div>
              <div className="mt-0.5 grid grid-cols-3 gap-1 text-center text-[10px] text-gray-400">
                <span>{a.uniqueEndpoints} endpoints</span>
                <span>{a.uniqueIps} IPs</span>
                <span className={a.errorCount > 0 ? "text-red-400" : ""}>{a.errorCount} errors</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
