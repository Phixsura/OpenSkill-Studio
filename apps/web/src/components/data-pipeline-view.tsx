"use client";

interface PipelineStep { order: number; name: string; type: string; icon: string;
  status: string; recordsProcessed: number; durationMs: number; }
interface DataPipelineViewProps { name: string; steps: PipelineStep[]; progressPct: number;
  totalRecords: number; completed: number; }

const statusDot: Record<string, string> = {
  completed: "bg-green-500", running: "bg-blue-500 animate-pulse",
  pending: "bg-gray-300 dark:bg-gray-600", failed: "bg-red-500",
};

export function DataPipelineView({ name, steps, progressPct, totalRecords, completed }: DataPipelineViewProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">{name}</h3>
        <span className="text-xs text-gray-400">{completed}/{steps.length} steps · {totalRecords.toLocaleString()} records</span>
      </div>
      <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${progressPct}%` }} />
      </div>
      <div className="space-y-1">
        {steps.map(s => (
          <div key={s.order} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${statusDot[s.status] ?? ""}`} />
              <span>{s.icon}</span>
              <span className="text-sm">{s.name}</span>
            </div>
            <span className="text-xs text-gray-400">{s.recordsProcessed.toLocaleString()} rows · {s.durationMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
