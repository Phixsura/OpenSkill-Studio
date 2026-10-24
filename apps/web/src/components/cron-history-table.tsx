"use client";

interface CronExecution { jobName: string; status: string; durationMs: number; startedAt: string; }
interface CronHistoryTableProps { executions: CronExecution[]; successRate: number; avgDurationMs: number; }

export function CronHistoryTable({ executions, successRate, avgDurationMs }: CronHistoryTableProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Job History</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>{successRate}% success</span>
          <span>avg {avgDurationMs}ms</span>
        </div>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700 max-h-56 overflow-y-auto">
        {executions.map((e, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2">
            <div className="flex items-center gap-2">
              <span className={e.status === "success" ? "text-green-600" : "text-red-600"}>
                {e.status === "success" ? "✓" : "✗"}
              </span>
              <span className="text-sm font-mono">{e.jobName}</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-400">
              <span>{e.durationMs}ms</span>
              <span>{e.startedAt}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
