"use client";

interface Props { depth: number; maxQueue: number; nextPriority: number | null; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestQueuePriorityCard({ depth, maxQueue, nextPriority, appName }: Props) {
  const usagePct = maxQueue > 0 ? Math.round((depth / maxQueue) * 100) : 0;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📮 Priority Queue</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {depth}/{maxQueue}</p>
        </div>
        {nextPriority && <span className="rounded bg-blue-100 px-1.5 py-0.5 text-[9px] font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">P{nextPriority} next</span>}
      </div>
      <div className="h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
        <div className={`h-1.5 rounded-full ${usagePct > 80 ? "bg-red-500" : "bg-blue-500"}`} style={{ width: `${usagePct}%` }} />
      </div>
    </div>
  );
}
