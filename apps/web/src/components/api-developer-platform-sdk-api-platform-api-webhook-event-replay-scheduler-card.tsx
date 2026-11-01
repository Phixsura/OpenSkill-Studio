"use client";

interface JobInfo { job_id: string; destination: string; total: number; replayed: number; failed_count: number; status: string; progress_pct: number; }
interface Props { jobs: JobInfo[]; activeCount: number; appName: string; }

const sDot: Record<string, string> = { pending: "bg-gray-400", running: "bg-blue-500", completed: "bg-green-500", failed: "bg-red-500" };

export default function APIDeveloperPlatformSDKApiPlatformApiWebhookEventReplaySchedulerCard({ jobs, activeCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Replay Scheduler</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {activeCount > 0 && <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] text-blue-700">{activeCount} active</span>}
      </div>
      {jobs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No replay jobs</p>
      ) : (
        <div className="space-y-2">
          {jobs.slice(0, 5).map((j) => (
            <div key={j.job_id}>
              <div className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-1.5">
                  <span className={`h-1.5 w-1.5 rounded-full ${sDot[j.status] ?? "bg-gray-400"}`} />
                  <span className="text-gray-700 dark:text-gray-300">{j.job_id}</span>
                </div>
                <span className="text-gray-400">{j.replayed}/{j.total} · {j.progress_pct}%</span>
              </div>
              <div className="mt-0.5 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1.5 rounded-full ${j.status === "failed" ? "bg-red-500" : "bg-blue-500"}`} style={{ width: `${j.progress_pct}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
