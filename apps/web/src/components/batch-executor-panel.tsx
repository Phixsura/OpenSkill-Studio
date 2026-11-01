"use client";

interface BatchOperation {
  opId: string;
  name: string;
  status: "pending" | "success" | "failed" | "skipped";
  durationMs: number;
  error?: string;
}

interface BatchSummary {
  status: "pending" | "running" | "completed" | "partial" | "failed";
  total: number;
  succeeded: number;
  failed: number;
  skipped: number;
  durationMs: number;
}

const opStatusConfig: Record<string, { icon: string; color: string }> = {
  pending: { icon: "⏳", color: "text-gray-400" },
  success: { icon: "✅", color: "text-green-600" },
  failed: { icon: "❌", color: "text-red-600" },
  skipped: { icon: "⏭", color: "text-gray-400" },
};

const batchStatusColors: Record<string, string> = {
  completed: "text-green-600", partial: "text-yellow-600", failed: "text-red-600",
  running: "text-blue-600", pending: "text-gray-500",
};

export function BatchExecutorPanel({
  operations,
  summary,
  onExecute,
}: {
  operations: BatchOperation[];
  summary: BatchSummary;
  onExecute?: () => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">⚡ Batch Executor</h2>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-bold capitalize ${batchStatusColors[summary.status]}`}>{summary.status}</span>
          {summary.status === "pending" && (
            <button onClick={onExecute} className="text-sm bg-green-600 text-white px-3 py-1.5 rounded-lg">Execute</button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-4 gap-2 text-center text-xs">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Total</span>
          <span className="font-bold text-lg">{summary.total}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Success</span>
          <span className="font-bold text-lg text-green-600">{summary.succeeded}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Failed</span>
          <span className="font-bold text-lg text-red-600">{summary.failed}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Time</span>
          <span className="font-bold text-lg">{summary.durationMs}ms</span>
        </div>
      </div>

      <div className="space-y-0.5">
        {operations.map((op) => {
          const cfg = opStatusConfig[op.status];
          return (
            <div key={op.opId} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span>{cfg.icon}</span>
                <span className="text-sm font-medium">{op.name}</span>
                {op.error && <span className="text-xs text-red-500">{op.error}</span>}
              </div>
              {op.durationMs > 0 && <span className="text-xs text-gray-400">{op.durationMs}ms</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
