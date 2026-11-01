"use client";

interface BatchInfo {
  batch_id: string;
  destination: string;
  event_count: number;
  flushed: boolean;
  delivered: boolean;
}

interface WebhookBatchCardProps {
  batches: BatchInfo[];
  pendingCount: number;
  appName: string;
}

export default function WebhookBatchCard({
  batches,
  pendingCount,
  appName,
}: WebhookBatchCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            📦 Webhook Batches
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{batches.length} batches</span>
          {pendingCount > 0 && (
            <p className="text-[10px] text-orange-500">{pendingCount} pending</p>
          )}
        </div>
      </div>

      {batches.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No batches</p>
      ) : (
        <div className="space-y-1.5">
          {batches.map((b) => (
            <div
              key={b.batch_id}
              className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`h-2 w-2 rounded-full ${b.delivered ? "bg-green-500" : b.flushed ? "bg-blue-500" : "bg-yellow-500"}`}
                />
                <span className="max-w-[150px] truncate text-[11px] text-gray-600 dark:text-gray-400">
                  {b.destination}
                </span>
              </div>
              <span className="text-[10px] text-gray-400">{b.event_count} events</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
