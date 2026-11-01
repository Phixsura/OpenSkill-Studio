"use client";

interface ReleaseInfo { version: string; release_date: string; entry_count: number; breaking_count: number; }
interface Props { releases: ReleaseInfo[]; totalReleases: number; totalEntries: number; appName: string; }

export default function APIDeveloperAPIChangelogReleaseTrackerCard({ releases, totalReleases, totalEntries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚀 Release Tracker</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{totalReleases} releases · {totalEntries} entries</span>
      </div>
      {releases.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No releases tracked</p>
      ) : (
        <div className="space-y-1">
          {releases.slice(0, 5).map((r) => (
            <div key={r.version} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="font-mono font-medium text-gray-800 dark:text-gray-200">{r.version}</span>
                <span className="text-gray-400">{r.release_date}</span>
              </div>
              <span className="text-gray-400">{r.entry_count} entries{r.breaking_count > 0 ? ` · ${r.breaking_count} breaking` : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
