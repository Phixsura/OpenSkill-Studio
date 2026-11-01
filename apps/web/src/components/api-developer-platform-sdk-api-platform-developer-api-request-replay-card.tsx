"use client";

interface ReplayStats { captured: number; replayed: number; successful: number; }
interface RecentCapture { request_id: string; method: string; path: string; original_status: number; }
interface Props { stats: ReplayStats; recent: RecentCapture[]; appName: string; }

const statusColor = (s: number) => s < 400 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400";

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiRequestReplayCard({ stats, recent, appName }: Props) {
  const successRate = stats.replayed > 0 ? ((stats.successful / stats.replayed) * 100).toFixed(1) : "—";
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Request Replay</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{successRate}% success</span>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{stats.captured}</div><div className="text-gray-400">Captured</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{stats.replayed}</div><div className="text-gray-400">Replayed</div></div>
        <div><div className="font-semibold text-green-600 dark:text-green-400">{stats.successful}</div><div className="text-gray-400">Success</div></div>
      </div>
      {recent.length > 0 && (
        <div className="space-y-1">
          {recent.map((r) => (
            <div key={r.request_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-gray-500">{r.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{r.path}</span>
              </div>
              <span className={statusColor(r.original_status)}>{r.original_status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
