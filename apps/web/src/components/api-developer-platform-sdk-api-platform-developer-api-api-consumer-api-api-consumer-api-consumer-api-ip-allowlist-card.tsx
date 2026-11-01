"use client";

interface Entry { id: string; cidr: string; label: string; addedAt: string; }
interface Props { entries: Entry[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIpAllowlistCard({ entries, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🛡️ IP Allowlist</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {entries.length} entries</p>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No IP restrictions (all IPs allowed)</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e) => (
            <div key={e.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[11px] dark:bg-gray-800">
              <div>
                <code className="font-medium text-gray-700 dark:text-gray-300">{e.cidr}</code>
                {e.label && <span className="ml-2 text-[10px] text-gray-400">{e.label}</span>}
              </div>
              <span className="text-[10px] text-gray-400">{e.addedAt}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
