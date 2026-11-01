"use client";

interface QueueStats { queued: number; processing: number; completed: number; failed: number; }
interface Props { stats: QueueStats; maxSize: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestQueueCard({ stats, maxSize, appName }: Props) {
  const depth = stats.queued + stats.processing;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📬 Request Queue</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {depth}/{maxSize} active</p>
        </div>
      </div>
      <div className="grid grid-cols-4 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-yellow-600">{stats.queued}</div><div className="text-gray-400">Queued</div></div>
        <div><div className="font-semibold text-blue-600">{stats.processing}</div><div className="text-gray-400">Processing</div></div>
        <div><div className="font-semibold text-green-600">{stats.completed}</div><div className="text-gray-400">Done</div></div>
        <div><div className="font-semibold text-red-600">{stats.failed}</div><div className="text-gray-400">Failed</div></div>
      </div>
    </div>
  );
}
