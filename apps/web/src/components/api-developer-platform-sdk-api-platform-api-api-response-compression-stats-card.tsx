"use client";

interface StatsInfo { endpoint: string; savings_pct: number; compression_rate: number; bandwidth_saved_bytes: number; total_responses: number; }
interface Props { stats: StatsInfo[]; totalSavingsBytes: number; appName: string; }

function fmtSize(b: number) { return b < 1024 ? `${b}B` : b < 1048576 ? `${(b/1024).toFixed(1)}KB` : `${(b/1048576).toFixed(1)}MB`; }

export default function APIDeveloperPlatformSDKApiPlatformApiApiResponseCompressionStatsCard({ stats, totalSavingsBytes, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗜️ Compression Stats</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-green-600">{fmtSize(totalSavingsBytes)} saved</span>
      </div>
      {stats.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No compression data</p>
      ) : (
        <div className="space-y-1.5">
          {stats.map((s) => (
            <div key={s.endpoint} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.endpoint}</span>
              <span className="text-green-600 font-bold">{s.savings_pct}% saved</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
