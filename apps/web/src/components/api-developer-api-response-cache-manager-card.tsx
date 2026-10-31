"use client";

interface StatsInfo { total_entries: number; hits: number; misses: number; hit_rate_pct: number; total_bytes: number; }
interface Props { stats: StatsInfo; appName: string; }

function fmtSize(b: number) { return b < 1024 ? `${b}B` : b < 1048576 ? `${(b/1024).toFixed(1)}KB` : `${(b/1048576).toFixed(1)}MB`; }

export default function APIDeveloperAPIResponseCacheManagerCard({ stats, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💾 Response Cache</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-lg font-bold ${stats.hit_rate_pct >= 80 ? "text-green-600" : stats.hit_rate_pct >= 50 ? "text-yellow-600" : "text-red-500"}`}>{stats.hit_rate_pct}%</span>
      </div>
      <div className="grid grid-cols-4 gap-2 text-center">
        {[
          { l: "Entries", v: stats.total_entries },
          { l: "Hits", v: stats.hits.toLocaleString() },
          { l: "Misses", v: stats.misses.toLocaleString() },
          { l: "Size", v: fmtSize(stats.total_bytes) },
        ].map((m) => (
          <div key={m.l} className="rounded bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-[11px] font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[8px] text-gray-400">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
