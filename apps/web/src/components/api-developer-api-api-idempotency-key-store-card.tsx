"use client";

interface StatsInfo { active_keys: number; total_hits: number; }
interface Props { stats: StatsInfo; appName: string; }

export default function APIDeveloperAPIApiIdempotencyKeyStoreCard({ stats, appName }: Props) {
  const hitRate = stats.active_keys > 0 ? Math.round(stats.total_hits / (stats.active_keys + stats.total_hits) * 100) : 0;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Idempotency Keys</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-blue-600">{stats.active_keys.toLocaleString()}</p>
          <p className="text-[9px] text-gray-400">Active</p>
        </div>
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-green-600">{stats.total_hits.toLocaleString()}</p>
          <p className="text-[9px] text-gray-400">Dedup Hits</p>
        </div>
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-purple-600">{hitRate}%</p>
          <p className="text-[9px] text-gray-400">Hit Rate</p>
        </div>
      </div>
    </div>
  );
}
