"use client";

interface TaskInfo { name: string; interval: number; enabled: boolean; runCount: number; handler: string; }
interface TaskSchedPanelProps { tasks: TaskInfo[]; totalExecutions: number; enabledCount: number; }

export function TaskSchedPanel({ tasks, totalExecutions, enabledCount }: TaskSchedPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏰ Task Scheduler</h3>
        <span className="text-xs text-gray-400">{enabledCount}/{tasks.length} enabled · {totalExecutions} runs</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {tasks.map(t => (
          <div key={t.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${t.enabled ? "bg-green-500" : "bg-gray-400"}`} />
              <span className="font-mono">{t.name}</span>
            </div>
            <div className="flex items-center gap-2 text-gray-400">
              <span>every {t.interval}s</span>
              <span>{t.runCount} runs</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
