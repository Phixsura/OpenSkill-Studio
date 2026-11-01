"use client";

interface VersionInfo { consumer_id: string; sdk_name: string; sdk_version: string; language: string; request_count: number; }
interface Props { versions: VersionInfo[]; outdatedCount: number; versionDistribution: Record<string, number>; appName: string; }

export default function APIDeveloperAPISDKVersionTrackerCard({ versions, outdatedCount, versionDistribution, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📦 SDK Version Tracker</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {versions.length} consumers</p>
        </div>
        {outdatedCount > 0 && <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-[10px] text-yellow-700">{outdatedCount} outdated</span>}
      </div>
      <div className="mb-3 flex flex-wrap gap-1.5">
        {Object.entries(versionDistribution).map(([ver, count]) => (
          <span key={ver} className="rounded bg-blue-50 px-2 py-0.5 text-[10px] text-blue-700 dark:bg-blue-900 dark:text-blue-200">v{ver}: {count}</span>
        ))}
      </div>
      {versions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No SDK usage tracked</p>
      ) : (
        <div className="space-y-1">
          {versions.slice(0, 5).map((v) => (
            <div key={v.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{v.consumer_id}</span>
              <span className="text-gray-400">v{v.sdk_version} · {v.language}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
