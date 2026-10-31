"use client";

interface Props { queueSize: number; maxSize: number; processedCount: number; topPriority: number | null; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestPriorityQueueCard({ queueSize, maxSize, processedCount, topPriority, appName }: Props) {
  const pct = maxSize > 0 ? Math.round((queueSize / maxSize) * 100) : 0;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Priority Queue</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div className="rounded bg-blue-50 p-1.5 dark:bg-blue-900/20"><div className="font-bold text-blue-600">{queueSize}</div><div className="text-[10px] text-gray-400">Queued</div></div>
        <div className="rounded bg-green-50 p-1.5 dark:bg-green-900/20"><div className="font-bold text-green-600">{processedCount.toLocaleString()}</div><div className="text-[10px] text-gray-400">Processed</div></div>
        <div className="rounded bg-gray-100 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-600">{topPriority ?? "—"}</div><div className="text-[10px] text-gray-400">Top Priority</div></div>
      </div>
      <div>
        <div className="flex justify-between text-[10px] text-gray-400"><span>Capacity</span><span>{queueSize}/{maxSize}</span></div>
        <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className={`h-full rounded-full ${pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-amber-500" : "bg-blue-500"}`} style={{ width: `${Math.min(pct, 100)}%` }} />
        </div>
      </div>
    </div>
  );
}
