"use client";

interface FailedDeliveryInfo {
  delivery_id: string;
  event_type: string;
  destination: string;
  original_status: number;
  replay_count: number;
  resolved: boolean;
}

interface WebhookReplayCardProps {
  deliveries: FailedDeliveryInfo[];
  pendingCount: number;
  resolvedCount: number;
  appName: string;
}

export default function WebhookReplayCard({ deliveries, pendingCount, resolvedCount, appName }: WebhookReplayCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔁 Webhook Replay</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{pendingCount} pending · {resolvedCount} resolved</span>
      </div>

      {deliveries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No failed deliveries</p>
      ) : (
        <div className="space-y-1.5">
          {deliveries.map((d) => (
            <div key={d.delivery_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${d.resolved ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-xs text-gray-700 dark:text-gray-300">{d.event_type}</span>
                <span className="text-[10px] text-red-500">{d.original_status}</span>
              </div>
              <span className="text-[10px] text-gray-400">{d.replay_count} retries</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
