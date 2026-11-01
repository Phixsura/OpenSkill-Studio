"use client";

interface CronJob {
  id: string;
  name: string;
  expression: string;
  command: string;
  status: "active" | "paused" | "disabled";
  runCount: number;
  failureCount: number;
  nextRunAt?: string;
  lastRunAt?: string;
}

const statusConfig: Record<string, { color: string; icon: string }> = {
  active: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", icon: "▶" },
  paused: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", icon: "⏸" },
  disabled: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", icon: "⊘" },
};

export function CronJobPanel({
  jobs,
  onPause,
  onResume,
  onDelete,
}: {
  jobs: CronJob[];
  onPause?: (id: string) => void;
  onResume?: (id: string) => void;
  onDelete?: (id: string) => void;
}) {
  const active = jobs.filter((j) => j.status === "active").length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">⏰ Cron Jobs</h2>
        <span className="text-sm text-gray-500">{active}/{jobs.length} active</span>
      </div>

      <div className="space-y-2">
        {jobs.map((job) => {
          const cfg = statusConfig[job.status];
          return (
            <div key={job.id} className={`rounded-xl border dark:border-gray-700 p-3 ${job.status === "disabled" ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span>{cfg.icon}</span>
                  <span className="font-semibold text-sm">{job.name}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{job.status}</span>
                  <code className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{job.expression}</code>
                </div>
                <div className="flex gap-1">
                  {job.status === "active" && (
                    <button onClick={() => onPause?.(job.id)} className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">Pause</button>
                  )}
                  {job.status === "paused" && (
                    <button onClick={() => onResume?.(job.id)} className="text-xs bg-green-600 text-white px-2 py-1 rounded">Resume</button>
                  )}
                  <button onClick={() => onDelete?.(job.id)} className="text-xs text-red-500">✕</button>
                </div>
              </div>
              <div className="flex gap-3 text-xs text-gray-500">
                <code>{job.command}</code>
                <span>×{job.runCount}</span>
                {job.failureCount > 0 && <span className="text-red-500">{job.failureCount} failures</span>}
                {job.nextRunAt && <span>next: {job.nextRunAt}</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
