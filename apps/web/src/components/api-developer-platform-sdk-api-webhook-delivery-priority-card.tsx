"use client";

interface QueueInfo { destination: string; queued: Record<string, number>; delivered: Record<string, number>; total_queued: number; total_delivered: number; }
interface Props { queues: QueueInfo[]; appName: string; }

const pColor: Record<string, string> = { critical: "bg-red-500", high: "bg-orange-500", normal: "bg-blue-500", low: "bg-gray-400", bulk: "bg-gray-300" };

export default function APIDeveloperPlatformSDKApiWebhookDeliveryPriorityCard({ queues, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚦 Delivery Priority</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      {queues.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No priority queues</p>
      ) : (
        <div className="space-y-2">
          {queues.map((q) => (
            <div key={q.destination} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{new URL(q.destination).hostname}</span>
                <span className="text-gray-400">{q.total_queued} queued · {q.total_delivered} delivered</span>
              </div>
              <div className="mt-1 flex gap-0.5">
                {["critical", "high", "normal", "low", "bulk"].map((p) => (
                  <div key={p} className={`h-2 rounded ${pColor[p]}`} style={{ width: `${Math.max(q.queued[p] ?? 0, 2)}px`, minWidth: q.queued[p] ? "4px" : "0" }} title={`${p}: ${q.queued[p] ?? 0}`} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
