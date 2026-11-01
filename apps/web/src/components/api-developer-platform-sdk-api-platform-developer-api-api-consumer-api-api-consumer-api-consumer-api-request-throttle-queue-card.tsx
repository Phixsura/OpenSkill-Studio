"use client";

interface Props { consumerId: string; queued: number; processing: number; completed: number; dropped: number; maxQueueSize: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestThrottleQueueCard({ consumerId, queued, processing, completed, dropped, maxQueueSize, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏳ Throttle Queue</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · Max: {maxQueueSize}</p>
      </div>
      <div className="grid grid-cols-4 gap-2 text-center text-[11px]">
        <div className="rounded bg-blue-50 p-1.5 dark:bg-blue-900/20"><div className="font-bold text-blue-600">{queued}</div><div className="text-[10px] text-gray-400">Queued</div></div>
        <div className="rounded bg-amber-50 p-1.5 dark:bg-amber-900/20"><div className="font-bold text-amber-600">{processing}</div><div className="text-[10px] text-gray-400">Active</div></div>
        <div className="rounded bg-green-50 p-1.5 dark:bg-green-900/20"><div className="font-bold text-green-600">{completed}</div><div className="text-[10px] text-gray-400">Done</div></div>
        <div className="rounded bg-red-50 p-1.5 dark:bg-red-900/20"><div className="font-bold text-red-600">{dropped}</div><div className="text-[10px] text-gray-400">Dropped</div></div>
      </div>
      {queued > 0 && (
        <div className="mt-2">
          <div className="h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
            <div className="h-full rounded-full bg-blue-500" style={{ width: `${Math.min((queued / maxQueueSize) * 100, 100)}%` }} />
          </div>
          <div className="mt-0.5 text-right text-[9px] text-gray-400">{queued}/{maxQueueSize}</div>
        </div>
      )}
    </div>
  );
}
