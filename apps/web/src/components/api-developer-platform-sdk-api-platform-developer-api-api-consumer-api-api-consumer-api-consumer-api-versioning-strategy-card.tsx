"use client";

interface Version { version: string; status: string; releasedAt: string; }
interface Props { versions: Version[]; strategyType: string; defaultVersion: string; pinnedVersion: string | null; appName: string; }

const statusColors: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  deprecated: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  sunset: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiVersioningStrategyCard({ versions, strategyType, defaultVersion, pinnedVersion, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔢 API Versioning</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — Strategy: {strategyType} · Default: {defaultVersion}</p>
      </div>
      {pinnedVersion && <div className="mb-2 rounded bg-blue-50 px-2 py-1 text-[11px] text-blue-700 dark:bg-blue-900/20 dark:text-blue-400">📌 Pinned to {pinnedVersion}</div>}
      {versions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No versions</p>
      ) : (
        <div className="space-y-1">
          {versions.map((v) => (
            <div key={v.version} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[11px] dark:bg-gray-800">
              <span className="font-bold text-gray-700 dark:text-gray-300">{v.version}</span>
              <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusColors[v.status] ?? ""}`}>{v.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
