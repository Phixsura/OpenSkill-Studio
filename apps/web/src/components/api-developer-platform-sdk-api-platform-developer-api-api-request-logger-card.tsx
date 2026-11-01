"use client";

interface LogStats { total: number; errors: number; avg_duration_ms: number; total_bytes_in: number; total_bytes_out: number; }
interface Props { stats: LogStats; errorRate: number; appName: string; }

const fmtBytes = (b: number) => b >= 1048576 ? `${(b / 1048576).toFixed(1)} MB` : b >= 1024 ? `${(b / 1024).toFixed(0)} KB` : `${b} B`;

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestLoggerCard({ stats, errorRate, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📝 Request Logger</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${errorRate < 1 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>{errorRate}% errors</span>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{stats.total.toLocaleString()}</div><div className="text-gray-400">Total</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{stats.avg_duration_ms}ms</div><div className="text-gray-400">Avg Latency</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{fmtBytes(stats.total_bytes_in)}</div><div className="text-gray-400">In</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{fmtBytes(stats.total_bytes_out)}</div><div className="text-gray-400">Out</div></div>
      </div>
    </div>
  );
}
