"use client";

interface BatchInfo {
  batch_id: string;
  status: "queued" | "processing" | "completed" | "failed" | "partially_failed";
  total: number;
  processed: number;
  succeeded: number;
  failed: number;
  progress_pct: number;
  created_at: string;
}

interface BatchProcessorCardProps {
  batches: BatchInfo[];
  appName: string;
}

const STATUS_STYLES: Record<string, { icon: string; text: string }> = {
  queued: { icon: "⏳", text: "text-gray-500" },
  processing: { icon: "⚙️", text: "text-blue-600 dark:text-blue-400" },
  completed: { icon: "✅", text: "text-green-600 dark:text-green-400" },
  failed: { icon: "❌", text: "text-red-600 dark:text-red-400" },
  partially_failed: { icon: "⚠️", text: "text-yellow-600 dark:text-yellow-400" },
};

function ProgressBar({ pct, status }: { pct: number; status: string }) {
  const color =
    status === "failed"
      ? "bg-red-500"
      : status === "partially_failed"
        ? "bg-yellow-500"
        : "bg-green-500";
  return (
    <div className="h-1.5 w-full rounded-full bg-gray-200 dark:bg-gray-700">
      <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${Math.min(pct, 100)}%` }} />
    </div>
  );
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  return `${Math.floor(diff / 3_600_000)}h ago`;
}

export default function BatchProcessorCard({ batches, appName }: BatchProcessorCardProps) {
  const activeCount = batches.filter(
    (b) => b.status === "processing" || b.status === "queued",
  ).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Batch Jobs</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {activeCount > 0 && (
          <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
            {activeCount} active
          </span>
        )}
      </div>

      {batches.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No batch jobs</p>
      ) : (
        <div className="space-y-2.5">
          {batches.map((b) => {
            const st = STATUS_STYLES[b.status] ?? STATUS_STYLES.queued;
            return (
              <div
                key={b.batch_id}
                className="rounded-lg border border-gray-100 px-3 py-2.5 dark:border-gray-800"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span>{st.icon}</span>
                    <span className="font-mono text-sm text-gray-800 dark:text-gray-200">
                      {b.batch_id}
                    </span>
                  </div>
                  <span className="text-[11px] text-gray-400">{timeAgo(b.created_at)}</span>
                </div>
                <div className="mt-1.5">
                  <ProgressBar pct={b.progress_pct} status={b.status} />
                </div>
                <div className="mt-1 flex items-center justify-between text-[11px] text-gray-400">
                  <span>
                    {b.processed}/{b.total} items · {b.progress_pct.toFixed(0)}%
                  </span>
                  <span>
                    {b.succeeded > 0 && (
                      <span className="text-green-600 dark:text-green-400">{b.succeeded} ok</span>
                    )}
                    {b.succeeded > 0 && b.failed > 0 && " · "}
                    {b.failed > 0 && <span className="text-red-500">{b.failed} failed</span>}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
