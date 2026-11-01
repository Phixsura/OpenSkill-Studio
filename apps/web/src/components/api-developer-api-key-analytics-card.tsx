"use client";

interface KeyInfo { key_id: string; total_requests: number; error_rate: number; avg_latency_ms: number; top_endpoint: string; }
interface Props { keys: KeyInfo[]; appName: string; }

export default function APIDeveloperAPIKeyAnalyticsCard({ keys, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Key Analytics</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{keys.length} keys</span>
      </div>
      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No key analytics</p>
      ) : (
        <div className="space-y-1.5">
          {keys.map((k) => (
            <div key={k.key_id} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{k.key_id}</span>
              <span className="text-gray-400">{k.total_requests} reqs · {k.error_rate}% err · {k.avg_latency_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
