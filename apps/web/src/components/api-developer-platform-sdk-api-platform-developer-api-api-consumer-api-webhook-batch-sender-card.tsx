"use client";

interface Stats { total: number; pending: number; success: number; failed: number; total_events: number; }
interface Props { stats: Stats; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookBatchSenderCard({ stats, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📦 Batch Sender</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {stats.pending > 0 && <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-[10px] font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">{stats.pending} pending</span>}
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{stats.total}</div><div className="text-gray-400">Batches</div></div>
        <div><div className="font-semibold text-green-600 dark:text-green-400">{stats.success}</div><div className="text-gray-400">Success</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{stats.total_events.toLocaleString()}</div><div className="text-gray-400">Events</div></div>
      </div>
    </div>
  );
}
