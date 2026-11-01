"use client";

interface Queue { name: string; pending: number; processing: number; failed: number;
  completed: number; throughput_per_min: number; eta_min: number; healthy: boolean; }
interface QueueMonitorDashboardProps { queues: Queue[]; totalBacklog: number; allHealthy: boolean; }

export function QueueMonitorDashboard({ queues, totalBacklog, allHealthy }: QueueMonitorDashboardProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Job Queues</h2>
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${allHealthy ? "bg-green-500" : "bg-red-500"}`} />
          <span className="text-xs text-gray-400">{totalBacklog} pending</span>
        </div>
      </div>
      {queues.map(q => (
        <div key={q.name} className={`rounded-lg border p-3 ${q.healthy ? "dark:border-gray-700" : "border-red-300 dark:border-red-700"}`}>
          <div className="flex items-center justify-between">
            <span className="font-medium">{q.name}</span>
            <span className="text-xs text-gray-400">{q.throughput_per_min}/min</span>
          </div>
          <div className="mt-2 grid grid-cols-4 gap-2 text-center text-xs">
            <div><p className="font-bold text-yellow-500">{q.pending}</p><p className="text-gray-400">Pending</p></div>
            <div><p className="font-bold text-blue-500">{q.processing}</p><p className="text-gray-400">Active</p></div>
            <div><p className="font-bold text-green-500">{q.completed}</p><p className="text-gray-400">Done</p></div>
            <div><p className={`font-bold ${q.failed > 0 ? "text-red-500" : "text-gray-400"}`}>{q.failed}</p><p className="text-gray-400">Failed</p></div>
          </div>
          {q.eta_min > 0 && <p className="mt-1 text-xs text-gray-400">ETA: {q.eta_min} min</p>}
        </div>
      ))}
    </div>
  );
}
