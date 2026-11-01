"use client";

interface QueueStats {
  queued: number;
  delivering: number;
  delivered: number;
  failed: number;
  dead_letter: number;
}

interface WebhookQueueCardProps {
  stats: QueueStats;
  queueDepth: number;
  deadLetterCount: number;
  appName: string;
}

export default function WebhookQueueCard({
  stats,
  queueDepth,
  deadLetterCount,
  appName,
}: WebhookQueueCardProps) {
  const total =
    stats.queued + stats.delivering + stats.delivered + stats.failed + stats.dead_letter;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            📤 Webhook Queue
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{total} total</span>
          {deadLetterCount > 0 && (
            <p className="text-[10px] text-red-500">{deadLetterCount} dead letters</p>
          )}
        </div>
      </div>

      <div className="mb-3 grid grid-cols-3 gap-2 text-center">
        <div className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
          <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{queueDepth}</p>
          <p className="text-[9px] text-gray-500">queued</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
          <p className="text-sm font-bold text-green-600">{stats.delivered}</p>
          <p className="text-[9px] text-gray-500">delivered</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
          <p className="text-sm font-bold text-red-500">{stats.dead_letter}</p>
          <p className="text-[9px] text-gray-500">dead letter</p>
        </div>
      </div>
    </div>
  );
}
