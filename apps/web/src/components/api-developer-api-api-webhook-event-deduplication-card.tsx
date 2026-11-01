"use client";

interface StatsInfo { active_hashes: number; duplicates_caught: number; }
interface Props { stats: StatsInfo; appName: string; }

export default function APIDeveloperAPIApiWebhookEventDeduplicationCard({ stats, appName }: Props) {
  const dedupRate = stats.active_hashes + stats.duplicates_caught > 0 ? Math.round(stats.duplicates_caught / (stats.active_hashes + stats.duplicates_caught) * 100) : 0;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Event Deduplication</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-blue-600">{stats.active_hashes.toLocaleString()}</p>
          <p className="text-[9px] text-gray-400">Active Hashes</p>
        </div>
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-green-600">{stats.duplicates_caught.toLocaleString()}</p>
          <p className="text-[9px] text-gray-400">Dupes Caught</p>
        </div>
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-purple-600">{dedupRate}%</p>
          <p className="text-[9px] text-gray-400">Dedup Rate</p>
        </div>
      </div>
    </div>
  );
}
