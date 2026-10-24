"use client";
interface QueueInfo { subscriberId: string; depth: number; }
interface WhQueueMgrPanelProps { queues: QueueInfo[]; totalQueued: number; processed: number; }
export function WhQueueMgrPanel({ queues, totalQueued, processed }: WhQueueMgrPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📬 Webhook Queues</h3>
        <span className="text-xs text-gray-400">{totalQueued} queued · {processed.toLocaleString()} processed</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {queues.map(q => (
          <div key={q.subscriberId} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{q.subscriberId}</span>
            <span className="text-gray-400">{q.depth} pending</span>
          </div>
        ))}
      </div>
    </div>
  );
}
