"use client";
interface Task { name: string; schedule: string; enabled: boolean; runs: number; }
interface SchedExecPanelProps { tasks: Task[]; totalRuns: number; enabled: number; }
export function SchedExecPanel({ tasks, totalRuns, enabled }: SchedExecPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏰ Scheduled Tasks</h3>
        <span className="text-xs text-gray-400">{enabled}/{tasks.length} enabled · {totalRuns} runs</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {tasks.map(t => (
          <div key={t.name} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${t.enabled ? "bg-green-500" : "bg-gray-400"}`} />
              <span className="font-mono">{t.name}</span>
            </div>
            <span className="text-gray-400">{t.schedule} · {t.runs} runs</span>
          </div>
        ))}
      </div>
    </div>
  );
}
