"use client";

interface BatchResult { item: string; status: string; reason: string | null; }
interface BatchOperationsPanelProps { action: string; results: BatchResult[];
  succeeded: number; failed: number; skipped: number; total: number; dryRun: boolean; }

const statusColors: Record<string, string> = {
  success: "text-green-600", failed: "text-red-600", skipped: "text-gray-400",
};

export function BatchOperationsPanel({ action, results, succeeded, failed, skipped, total, dryRun }: BatchOperationsPanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold capitalize">{action}</h3>
        <div className="flex gap-3 text-xs">
          {dryRun && <span className="rounded bg-yellow-100 px-2 py-0.5 text-yellow-700 dark:bg-yellow-900/30">Dry Run</span>}
          <span className="text-green-600">{succeeded}✓</span>
          <span className="text-red-600">{failed}✗</span>
          {skipped > 0 && <span className="text-gray-400">{skipped} skipped</span>}
        </div>
      </div>
      <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-full rounded-full bg-green-500" style={{ width: `${(succeeded / Math.max(total, 1)) * 100}%` }} />
      </div>
      <div className="max-h-48 overflow-y-auto divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {results.map((r, i) => (
          <div key={i} className="flex items-center justify-between px-3 py-1.5 text-sm">
            <span className="truncate font-mono text-xs">{r.item || "(empty)"}</span>
            <span className={`text-xs ${statusColors[r.status] ?? ""}`}>{r.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
