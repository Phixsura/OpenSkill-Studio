"use client";

interface BatchProgressBarProps { total: number; completed: number; failed: number; operation: string; }

export function BatchProgressBar({ total, completed, failed, operation }: BatchProgressBarProps) {
  const pct = Math.round((completed / Math.max(total, 1)) * 100);
  const isComplete = completed + failed >= total;

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">{operation}</h3>
        <span className="text-xs text-gray-400">{completed}/{total} {isComplete ? "✅" : "⏳"}</span>
      </div>
      <div className="mt-2 h-3 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${pct}%` }} />
      </div>
      {failed > 0 && <p className="mt-1 text-xs text-red-500">❌ {failed} failed</p>}
    </div>
  );
}
