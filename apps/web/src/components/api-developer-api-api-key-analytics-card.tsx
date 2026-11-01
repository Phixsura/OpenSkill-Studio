"use client";

interface KeyInfo { key_id: string; key_prefix: string; total_requests: number; error_count: number; endpoints_hit: Record<string, number>; }
interface Props { keys: KeyInfo[]; appName: string; }

export default function APIDeveloperAPIApiKeyAnalyticsCard({ keys, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 API Key Analytics</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {keys.length} keys tracked</p>
      </div>
      {keys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No API key usage</p>
      ) : (
        <div className="space-y-2">
          {keys.map((k) => (
            <div key={k.key_id} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
              <div>
                <span className="font-mono text-[11px] text-gray-700 dark:text-gray-300">{k.key_prefix}...</span>
                <p className="text-[10px] text-gray-400">{Object.keys(k.endpoints_hit).length} endpoints</p>
              </div>
              <div className="text-right">
                <span className="text-[11px] font-medium text-gray-900 dark:text-gray-100">{k.total_requests.toLocaleString()} reqs</span>
                {k.error_count > 0 && <p className="text-[10px] text-red-500">{k.error_count} errors</p>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
