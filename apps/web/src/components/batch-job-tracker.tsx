"use client";

interface BatchJob { jobId: string; name: string; itemCount: number;
  totalBatches: number; completedBatches: number; failedBatches: number; status: string; }
interface BatchJobTrackerProps { jobs: BatchJob[]; running: number; totalItems: number; }

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-gray-200 text-gray-600", running: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700", completed_with_errors: "bg-yellow-100 text-yellow-700",
};

export function BatchJobTracker({ jobs, running, totalItems }: BatchJobTrackerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚙️ Batch Jobs</h3>
        <span className="text-xs text-gray-400">{jobs.length} jobs · {running} running · {totalItems} items</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {jobs.map(j => {
          const done = j.completedBatches + j.failedBatches;
          const pct = j.totalBatches > 0 ? Math.round((done / j.totalBatches) * 100) : 0;
          return (
            <div key={j.jobId} className="px-4 py-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">{j.name}</span>
                <div className="flex gap-2">
                  <span className="text-xs text-gray-400">{pct}%</span>
                  <span className={`px-2 py-0.5 text-[10px] rounded-full ${STATUS_COLORS[j.status] ?? ""}`}>{j.status.replaceAll("_", " ")}</span>
                </div>
              </div>
              <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div className="h-full bg-blue-500 rounded-full" style={{ width: `${pct}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
