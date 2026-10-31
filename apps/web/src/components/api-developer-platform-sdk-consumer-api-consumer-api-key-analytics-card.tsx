"use client";

interface KeyStats { keyId: string; totalRequests: number; errorRate: number; avgLatencyMs: number; uniqueEndpoints: number; lastUsed: string | null; }
interface Props { keys: KeyStats[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiConsumerApiKeyAnalyticsCard({ keys, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Key Analytics</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {keys.length} keys</p>
      </div>
      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No key usage data</p>
      ) : (
        <div className="space-y-2">
          {keys.map((k) => (
            <div key={k.keyId} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="font-medium text-gray-700 dark:text-gray-300">{k.keyId}</code>
                <span className="text-gray-400">{k.totalRequests.toLocaleString()} req</span>
              </div>
              <div className="mt-0.5 grid grid-cols-3 gap-1 text-center text-[10px] text-gray-400">
                <span className={k.errorRate > 5 ? "text-red-500" : ""}>{k.errorRate}% err</span>
                <span>{k.avgLatencyMs}ms avg</span>
                <span>{k.uniqueEndpoints} endpoints</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
