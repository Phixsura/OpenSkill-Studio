"use client";

interface ConfigEntry { key: string; value: string; }
interface Props { entries: ConfigEntry[]; consumerId: string; version: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiTenantConfigCard({ entries, consumerId, version, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚙️ Tenant Config</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className="text-[10px] text-gray-400">v{version}</span>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No config overrides</p>
      ) : (
        <div className="space-y-1">
          {entries.map((e) => (
            <div key={e.key} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[11px] dark:bg-gray-800">
              <code className="text-gray-700 dark:text-gray-300">{e.key}</code>
              <span className="text-gray-500">{e.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
