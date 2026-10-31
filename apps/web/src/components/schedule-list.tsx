"use client";

interface Schedule { id: string; functionName: string; cron: string; enabled: boolean; lastRun: string | null; runCount: number; }

interface ScheduleListProps { schedules: Schedule[]; onToggle?: (id: string, enabled: boolean) => void; onDelete?: (id: string) => void; }

export function ScheduleList({ schedules, onToggle, onDelete }: ScheduleListProps) {
  if (schedules.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No scheduled executions</p>;
  return (
    <div className="space-y-2">
      {schedules.map(s => (
        <div key={s.id} className={`flex items-center justify-between rounded border p-3 ${s.enabled ? "border-green-200 dark:border-green-800" : "border-gray-200 opacity-60 dark:border-gray-700"}`}>
          <div>
            <span className="font-mono text-sm font-semibold">{s.functionName}</span>
            <span className="ml-2 text-xs text-gray-500">{s.cron}</span>
            <p className="text-xs text-gray-400">{s.runCount} runs{s.lastRun ? ` · Last: ${s.lastRun}` : ""}</p>
          </div>
          <div className="flex gap-2">
            {onToggle && <button onClick={() => onToggle(s.id, !s.enabled)} className="text-xs text-blue-600">{s.enabled ? "Disable" : "Enable"}</button>}
            {onDelete && <button onClick={() => onDelete(s.id)} className="text-xs text-red-500">Delete</button>}
          </div>
        </div>
      ))}
    </div>
  );
}
