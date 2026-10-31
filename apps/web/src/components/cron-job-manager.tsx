"use client";

interface CronJob { jobId: string; name: string; schedule: string; handler: string; enabled: boolean; runCount: number; }

export function CronJobManager({ jobs, onToggle, onTrigger, onDelete }: {
  jobs: CronJob[]; onToggle?: (id: string, enabled: boolean) => void;
  onTrigger?: (id: string) => void; onDelete?: (id: string) => void;
}) {
  if (!jobs.length) return <div className="text-center text-gray-400 py-6 text-sm">No scheduled jobs</div>;
  return (
    <div className="space-y-2">
      {jobs.map(j => (
        <div key={j.jobId} className={`border dark:border-gray-700 rounded-xl p-3 ${!j.enabled ? "opacity-50" : ""}`}>
          <div className="flex items-center justify-between">
            <div>
              <span className="font-medium text-sm">{j.name}</span>
              <div className="flex gap-2 mt-0.5">
                <code className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded font-mono">{j.schedule}</code>
                <span className="text-xs text-gray-500">{j.handler}</span>
                <span className="text-xs text-gray-400">{j.runCount} runs</span>
              </div>
            </div>
            <div className="flex gap-1">
              <button onClick={() => onTrigger?.(j.jobId)} className="text-xs bg-green-500 text-white px-2 py-1 rounded" disabled={!j.enabled}>▶</button>
              <button onClick={() => onToggle?.(j.jobId, !j.enabled)} className="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">
                {j.enabled ? "⏸" : "▶️"}
              </button>
              <button onClick={() => onDelete?.(j.jobId)} className="text-xs text-red-400 px-2 py-1">🗑</button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
