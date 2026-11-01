"use client";

interface VersionDistInfo {
  version: string;
  count: number;
  is_latest: boolean;
}

interface SDKVersionTrackerCardProps {
  versions: VersionDistInfo[];
  latestVersion: string;
  outdatedCount: number;
  totalInstallations: number;
  appName: string;
}

export default function SDKVersionTrackerCard({
  versions,
  latestVersion,
  outdatedCount,
  totalInstallations,
  appName,
}: SDKVersionTrackerCardProps) {
  const maxCount = Math.max(...versions.map((v) => v.count), 1);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">SDK Versions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded bg-blue-100 px-1.5 py-0.5 font-mono text-[10px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
            latest: v{latestVersion}
          </span>
          {outdatedCount > 0 && (
            <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">
              {outdatedCount} outdated
            </span>
          )}
        </div>
      </div>

      <p className="mb-3 text-xs text-gray-400">{totalInstallations} installations tracked</p>

      {versions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No SDK usage recorded</p>
      ) : (
        <div className="space-y-1.5">
          {versions.map((v) => (
            <div key={v.version} className="flex items-center gap-2">
              <span className="w-16 text-right font-mono text-[11px] text-gray-600 dark:text-gray-400">
                v{v.version}
              </span>
              <div className="h-4 flex-1 rounded bg-gray-100 dark:bg-gray-800">
                <div
                  className={`h-4 rounded ${v.is_latest ? "bg-green-500" : "bg-yellow-500"}`}
                  style={{ width: `${(v.count / maxCount) * 100}%` }}
                />
              </div>
              <span className="w-8 text-[11px] text-gray-500">{v.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
