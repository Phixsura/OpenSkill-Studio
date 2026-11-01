"use client";

interface VersionStat {
  version: string;
  requests: number;
  consumers: number;
  latest: boolean;
}

interface SDKVersionCardProps {
  versions: VersionStat[];
  outdatedCount: number;
  appName: string;
}

export default function SDKVersionCard({ versions, outdatedCount, appName }: SDKVersionCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            📦 SDK Versions
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{versions.length} versions</span>
          {outdatedCount > 0 && (
            <p className="text-[10px] text-orange-500">{outdatedCount} outdated</p>
          )}
        </div>
      </div>

      {versions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No SDK usage tracked</p>
      ) : (
        <div className="space-y-1.5">
          {versions.map((v) => (
            <div
              key={v.version}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">
                  {v.version}
                </span>
                {v.latest && (
                  <span className="rounded bg-green-100 px-1.5 py-0.5 text-[9px] font-medium text-green-700 dark:bg-green-900 dark:text-green-300">
                    latest
                  </span>
                )}
              </div>
              <span className="text-[10px] text-gray-400">
                {v.consumers} consumers · {v.requests} reqs
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
