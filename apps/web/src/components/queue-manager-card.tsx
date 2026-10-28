"use client";

interface QueueInfo {
  queue_name: string;
  pending: number;
  processing: number;
  completed: number;
  failed: number;
  dead_letter: number;
}

interface QueueManagerCardProps {
  queues: QueueInfo[];
  appName: string;
}

function formatNum(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

function StatusDot({ count, color, label }: { count: number; color: string; label: string }) {
  if (count === 0) return null;
  return (
    <span className={`inline-flex items-center gap-1 text-[11px] ${color}`}>
      <span className={`h-1.5 w-1.5 rounded-full bg-current`} />
      {formatNum(count)} {label}
    </span>
  );
}

export default function QueueManagerCard({ queues, appName }: QueueManagerCardProps) {
  const totalPending = queues.reduce((s, q) => s + q.pending, 0);
  const totalDL = queues.reduce((s, q) => s + q.dead_letter, 0);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Job Queues</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex gap-2">
          {totalPending > 0 && (
            <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
              {formatNum(totalPending)} pending
            </span>
          )}
          {totalDL > 0 && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              {totalDL} dead-letter
            </span>
          )}
        </div>
      </div>

      {queues.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No queues</p>
      ) : (
        <div className="space-y-3">
          {queues.map((q) => (
            <div
              key={q.queue_name}
              className="rounded-lg border border-gray-100 px-3 py-2.5 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-sm font-medium text-gray-800 dark:text-gray-200">
                  {q.queue_name}
                </span>
                <span className="text-[11px] text-gray-400">
                  {formatNum(q.completed)} processed
                </span>
              </div>
              <div className="mt-1.5 flex flex-wrap gap-3">
                <StatusDot
                  count={q.pending}
                  color="text-blue-600 dark:text-blue-400"
                  label="pending"
                />
                <StatusDot
                  count={q.processing}
                  color="text-yellow-600 dark:text-yellow-400"
                  label="active"
                />
                <StatusDot
                  count={q.failed}
                  color="text-orange-600 dark:text-orange-400"
                  label="failed"
                />
                <StatusDot
                  count={q.dead_letter}
                  color="text-red-600 dark:text-red-400"
                  label="dead"
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
