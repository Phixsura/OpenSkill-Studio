"use client";

interface StatsInfo { count: number; total_original: number; total_compressed: number; avg_savings_pct: number; }
interface Props { stats: StatsInfo; appName: string; }

function fmtSize(b: number) { return b < 1024 ? `${b}B` : b < 1048576 ? `${(b/1024).toFixed(1)}KB` : `${(b/1048576).toFixed(1)}MB`; }

export default function APIDeveloperAPIApiWebhookCompressionCard({ stats, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗜️ Webhook Compression</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-lg font-bold text-green-600">{stats.avg_savings_pct}%</span>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-[11px] font-bold text-gray-900 dark:text-gray-100">{stats.count.toLocaleString()}</p>
          <p className="text-[8px] text-gray-400">Compressed</p>
        </div>
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-[11px] font-bold text-gray-900 dark:text-gray-100">{fmtSize(stats.total_original)}</p>
          <p className="text-[8px] text-gray-400">Original</p>
        </div>
        <div className="rounded bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-[11px] font-bold text-green-600">{fmtSize(stats.total_compressed)}</p>
          <p className="text-[8px] text-gray-400">After</p>
        </div>
      </div>
    </div>
  );
}
