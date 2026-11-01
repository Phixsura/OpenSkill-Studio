"use client";

interface ReplayInfo { replay_id: string; consumer_id: string; status: string; response_status: number; }
interface Stats { total: number; pending: number; success: number; failed: number; }
interface Props { stats: Stats; recent: ReplayInfo[]; appName: string; }

const statusIcon: Record<string, string> = { pending: "⏳", success: "✅", failed: "❌" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookReplayCard({ stats, recent, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Webhook Replay</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {stats.pending > 0 && <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-[10px] font-medium text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">{stats.pending} pending</span>}
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{stats.total}</div><div className="text-gray-400">Total</div></div>
        <div><div className="font-semibold text-green-600 dark:text-green-400">{stats.success}</div><div className="text-gray-400">Success</div></div>
        <div><div className="font-semibold text-red-600 dark:text-red-400">{stats.failed}</div><div className="text-gray-400">Failed</div></div>
      </div>
      {recent.length > 0 && (
        <div className="space-y-1">
          {recent.map((r) => (
            <div key={r.replay_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{statusIcon[r.status] ?? "•"} {r.consumer_id}</span>
              {r.response_status > 0 && <span className="text-gray-400">{r.response_status}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
