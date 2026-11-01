"use client";

interface IpInfo { entry_id: string; network: string; label: string; }
interface Props { consumerId: string; entries: IpInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerIpAllowlistCard({ consumerId, entries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🛡️ IP Allowlist</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-xs text-gray-400">No IP restrictions (all IPs allowed)</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e) => (
            <div key={e.entry_id} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{e.network}</span>
              {e.label && <span className="text-gray-400">{e.label}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
