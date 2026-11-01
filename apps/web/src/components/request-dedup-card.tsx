"use client";

interface DedupStatsInfo {
  tracked: number;
  total_duplicates: number;
  ttl_seconds: number;
}

interface RequestDedupCardProps {
  stats: DedupStatsInfo;
  appName: string;
}

export default function RequestDedupCard({ stats, appName }: RequestDedupCardProps) {
  const dedupRate =
    stats.tracked > 0 && stats.total_duplicates > 0
      ? Math.round((stats.total_duplicates / (stats.tracked + stats.total_duplicates)) * 100)
      : 0;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Request Dedup</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-600 dark:bg-gray-800 dark:text-gray-400">
          {stats.ttl_seconds}s window
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3 text-center">
        <div>
          <p className="text-lg font-bold text-gray-800 dark:text-gray-200">{stats.tracked}</p>
          <p className="text-[10px] text-gray-500">Tracked</p>
        </div>
        <div>
          <p className="text-lg font-bold text-red-600 dark:text-red-400">
            {stats.total_duplicates}
          </p>
          <p className="text-[10px] text-gray-500">Duplicates</p>
        </div>
        <div>
          <p className="text-lg font-bold text-gray-800 dark:text-gray-200">{dedupRate}%</p>
          <p className="text-[10px] text-gray-500">Dedup Rate</p>
        </div>
      </div>
    </div>
  );
}
