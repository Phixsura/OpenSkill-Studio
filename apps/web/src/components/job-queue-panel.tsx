"use client";

interface JobInfo { id: string; status: string; priority: number; attempts: number; }
interface JobQueuePanelProps { jobs: JobInfo[]; pending: number; completed: number; failed: number; }

const STATUS_STYLE: Record<string, string> = {
  pending: "text-yellow-600", processing: "text-blue-500", completed: "text-green-600", failed: "text-red-600",
};

export function JobQueuePanel({ jobs, pending, completed, failed }: JobQueuePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Job Queue</h3>
        <span className="text-xs text-gray-400">{pending} pending · {completed} done · {failed} failed</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {jobs.map(j => (
          <div key={j.id} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{j.id}</span>
            <div className="flex items-center gap-2">
              <span className="text-gray-400">p:{j.priority} · #{j.attempts}</span>
              <span className={`font-bold ${STATUS_STYLE[j.status] ?? ""}`}>{j.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
