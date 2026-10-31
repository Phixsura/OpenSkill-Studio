"use client";

interface ScheduledTask { name: string; schedule: string; handler: string;
  enabled: boolean; runCount: number; lastStatus: string | null; }
interface TaskSchedulerPanelProps { tasks: ScheduledTask[];
  onRun: (name: string) => void; onToggle: (name: string) => void; }

export function TaskSchedulerPanel({ tasks, onRun, onToggle }: TaskSchedulerPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏰ Scheduled Tasks</h3>
        <span className="text-xs text-gray-400">{tasks.length} tasks</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {tasks.map(t => (
          <div key={t.name} className={`flex items-center justify-between px-4 py-3 ${!t.enabled ? "opacity-50" : ""}`}>
            <div>
              <div className="text-sm font-medium">{t.name}</div>
              <div className="text-[10px] text-gray-400 font-mono">{t.schedule} · {t.handler} · {t.runCount} runs</div>
            </div>
            <div className="flex gap-2">
              <button onClick={() => onRun(t.name)} disabled={!t.enabled}
                className="px-2 py-1 text-xs bg-blue-500 text-white rounded disabled:opacity-50">▶ Run</button>
              <button onClick={() => onToggle(t.name)}
                className={`px-2 py-1 text-xs rounded ${t.enabled ? "bg-green-100 text-green-700" : "bg-gray-200 text-gray-500"}`}>
                {t.enabled ? "On" : "Off"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
