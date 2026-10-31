"use client";

interface LogEntry { log_id: string; consumer_id: string; event_type: string; status_code: number; duration_ms: number; success: boolean; }
interface Stats { total: number; success: number; failed: number; success_rate: number; avg_duration_ms: number; }
interface Props { entries: LogEntry[]; stats: Stats; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerWebhookLogCard({ entries, stats, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Webhook Log</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${stats.success_rate >= 95 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>{stats.success_rate}%</span>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{stats.total.toLocaleString()}</div><div className="text-gray-400">Total</div></div>
        <div><div className="font-semibold text-green-600 dark:text-green-400">{stats.success}</div><div className="text-gray-400">Success</div></div>
        <div><div className="font-semibold text-red-600 dark:text-red-400">{stats.failed}</div><div className="text-gray-400">Failed</div></div>
      </div>
      {entries.length > 0 && (
        <div className="space-y-1">
          {entries.slice(0, 5).map((e) => (
            <div key={e.log_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{e.event_type}</span>
              <span className={e.success ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}>{e.status_code} · {Math.round(e.duration_ms)}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
