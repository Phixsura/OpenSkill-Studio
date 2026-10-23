"use client";

interface QueueItem { queue_id: string; content_type: string; content_id: string;
  reason: string; reported_by: string; status: string; created_at: string; }
interface ModerationQueuePanelProps { items: QueueItem[]; pendingCount: number;
  onApprove: (id: string) => void; onReject: (id: string) => void; }

const typeIcon: Record<string, string> = {
  review: "⭐", app_listing: "📦", profile: "👤", comment: "💬", screenshot: "🖼️",
};

export function ModerationQueuePanel({ items, pendingCount, onApprove, onReject }: ModerationQueuePanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Moderation Queue</h2>
        <span className="rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-700 dark:bg-yellow-900/30">
          {pendingCount} pending
        </span>
      </div>
      {items.map(i => (
        <div key={i.queue_id} className="rounded-lg border p-3 dark:border-gray-700">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <span>{typeIcon[i.content_type] ?? "📄"}</span>
              <div>
                <p className="text-sm font-medium capitalize">{i.content_type.replace("_", " ")}</p>
                <p className="text-xs text-gray-400">{i.reason}</p>
              </div>
            </div>
            <span className="text-xs text-gray-300">{i.reported_by}</span>
          </div>
          <div className="mt-2 flex gap-2">
            <button onClick={() => onApprove(i.queue_id)} className="rounded bg-green-600 px-3 py-1 text-xs text-white">Approve</button>
            <button onClick={() => onReject(i.queue_id)} className="rounded bg-red-600 px-3 py-1 text-xs text-white">Reject</button>
          </div>
        </div>
      ))}
    </div>
  );
}
