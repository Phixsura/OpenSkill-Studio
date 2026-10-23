"use client";

interface QueueStats { queue: string; total: number; byStatus: Record<string, number>; }
interface JobQueueDashboardProps { queues: QueueStats[]; }

const STATUS_COLOR: Record<string, string> = {
  pending: "bg-blue-500", completed: "bg-green-500", retrying: "bg-yellow-500", failed: "bg-red-500",
};

export function JobQueueDashboard({ queues }: JobQueueDashboardProps) {
  const totalJobs = queues.reduce((a, q) => a + q.total, 0);
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">⚙️ Job Queues</h3>
        <span className="text-xs text-gray-400">{totalJobs} total jobs</span>
      </div>
      <div className="space-y-4">
        {queues.map(q => (
          <div key={q.queue}>
            <div className="flex justify-between text-sm mb-1">
              <span className="font-medium">{q.queue}</span>
              <span className="text-gray-400">{q.total}</span>
            </div>
            <div className="flex h-3 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-800">
              {Object.entries(q.byStatus).map(([status, count]) => (
                <div key={status} className={STATUS_COLOR[status] || "bg-gray-400"}
                     style={{ width: `${(count / Math.max(q.total, 1)) * 100}%` }}
                     title={`${status}: ${count}`} />
              ))}
            </div>
            <div className="flex gap-3 mt-1 text-xs text-gray-400">
              {Object.entries(q.byStatus).map(([s, c]) => <span key={s}>{s}: {c}</span>)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
