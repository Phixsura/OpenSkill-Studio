"use client";

interface StatsInfo { active_keys: number; duplicate_hits: number; }
interface Props { stats: StatsInfo; appName: string; }

export default function APIDeveloperAPIApiRequestDeduplicationCard({ stats, appName }: Props) {
  const savingsRate = stats.active_keys > 0 ? Math.round(stats.duplicate_hits / (stats.active_keys + stats.duplicate_hits) * 100) : 0;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Request Deduplication</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-blue-600">{stats.active_keys.toLocaleString()}</p>
          <p className="text-[9px] text-gray-400">Active Keys</p>
        </div>
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-green-600">{stats.duplicate_hits.toLocaleString()}</p>
          <p className="text-[9px] text-gray-400">Dedup Hits</p>
        </div>
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-purple-600">{savingsRate}%</p>
          <p className="text-[9px] text-gray-400">Savings</p>
        </div>
      </div>
    </div>
  );
}
