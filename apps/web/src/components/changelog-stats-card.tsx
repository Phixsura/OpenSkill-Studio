"use client";

interface ChangelogStatsInfo {
  total_releases: number;
  total_entries: number;
  breaking_changes: number;
  avg_days_between_releases: number;
  top_contributors: [string, number][];
  categories: Record<string, number>;
}

interface ChangelogStatsCardProps {
  stats: ChangelogStatsInfo;
  appName: string;
}

export default function ChangelogStatsCard({ stats, appName }: ChangelogStatsCardProps) {
  const categories = Object.entries(stats.categories).sort((a, b) => b[1] - a[1]);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Changelog Stats
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
      </div>

      {/* Key metrics */}
      <div className="mb-4 grid grid-cols-4 gap-3 text-center">
        <div>
          <p className="text-lg font-bold text-gray-800 dark:text-gray-200">
            {stats.total_releases}
          </p>
          <p className="text-[10px] text-gray-500">Releases</p>
        </div>
        <div>
          <p className="text-lg font-bold text-gray-800 dark:text-gray-200">
            {stats.total_entries}
          </p>
          <p className="text-[10px] text-gray-500">Changes</p>
        </div>
        <div>
          <p className="text-lg font-bold text-red-600 dark:text-red-400">
            {stats.breaking_changes}
          </p>
          <p className="text-[10px] text-gray-500">Breaking</p>
        </div>
        <div>
          <p className="text-lg font-bold text-blue-600 dark:text-blue-400">
            {stats.avg_days_between_releases}d
          </p>
          <p className="text-[10px] text-gray-500">Cadence</p>
        </div>
      </div>

      {/* Categories */}
      {categories.length > 0 && (
        <div className="mb-3">
          <p className="mb-1 text-[10px] font-medium text-gray-500">Categories</p>
          <div className="flex flex-wrap gap-1.5">
            {categories.map(([cat, count]) => (
              <span
                key={cat}
                className="rounded-full bg-gray-100 px-2 py-0.5 text-[11px] text-gray-600 dark:bg-gray-800 dark:text-gray-400"
              >
                {cat} ({count})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Top contributors */}
      {stats.top_contributors.length > 0 && (
        <div>
          <p className="mb-1 text-[10px] font-medium text-gray-500">Top Contributors</p>
          <div className="flex flex-wrap gap-1.5">
            {stats.top_contributors.map(([name, count]) => (
              <span
                key={name}
                className="rounded-full bg-blue-100 px-2 py-0.5 text-[11px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
              >
                {name} ({count})
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
