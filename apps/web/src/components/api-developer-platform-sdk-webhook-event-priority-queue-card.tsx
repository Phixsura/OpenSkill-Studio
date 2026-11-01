"use client";

interface Props { queueSize: number; processedCount: number; priorityCounts: Record<string, number>; appName: string; }

const pColor: Record<string, string> = { critical: "text-red-600", high: "text-orange-600", normal: "text-blue-600", low: "text-gray-500" };

export default function APIDeveloperPlatformSDKWebhookEventPriorityQueueCard({ queueSize, processedCount, priorityCounts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏫ Event Priority Queue</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-blue-600">{queueSize} queued</span>
      </div>
      <div className="mb-3 flex gap-3 text-[10px]">
        {Object.entries(priorityCounts).map(([p, c]) => (
          <span key={p} className={pColor[p] ?? "text-gray-400"}>{p}: {c}</span>
        ))}
      </div>
      <p className="text-center text-[11px] text-gray-400">{processedCount.toLocaleString()} processed</p>
    </div>
  );
}
