"use client";

interface KeyInfo { key_id: string; consumer_id: string; total_requests: number; error_rate: number; endpoint_count: number; }
interface Props { keys: KeyInfo[]; totalKeys: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiKeyAnalyticsCard({ keys, totalKeys, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Key Analytics</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalKeys} keys tracked</p>
      </div>
      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No key analytics</p>
      ) : (
        <div className="space-y-1">
          {keys.map((k) => (
            <div key={k.key_id} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{k.key_id}</span>
              <span className="text-gray-400">{k.total_requests.toLocaleString()} reqs · {k.error_rate}% err · {k.endpoint_count} ep</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
