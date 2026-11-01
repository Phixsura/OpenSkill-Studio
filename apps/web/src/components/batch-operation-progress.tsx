"use client";

interface BatchOperationProgressProps { batchId: string; operation: string; total: number;
  completed: number; failed: number; progressPct: number; status: string; onCancel: () => void; }

export function BatchOperationProgress({ batchId, operation, total, completed, failed, progressPct, status, onCancel }: BatchOperationProgressProps) {
  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold capitalize">{operation} Batch</h3>
          <p className="font-mono text-xs text-gray-400">{batchId}</p>
        </div>
        <span className={`rounded-full px-2 py-0.5 text-xs ${status === "completed" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-blue-100 text-blue-700 dark:bg-blue-900/30"}`}>
          {status}
        </span>
      </div>
      <div className="mt-3">
        <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className="h-full rounded-full bg-blue-500 transition-all" style={{ width: `${progressPct}%` }} />
        </div>
        <div className="mt-1 flex justify-between text-xs text-gray-400">
          <span>{progressPct}%</span>
          <span>✅ {completed} · ❌ {failed} · ⏳ {total - completed - failed}</span>
        </div>
      </div>
      {status !== "completed" && (
        <button onClick={onCancel} className="mt-2 w-full rounded border border-red-300 py-1 text-xs text-red-600">Cancel</button>
      )}
    </div>
  );
}
