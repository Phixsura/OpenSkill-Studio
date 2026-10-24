"use client";

interface ExecutionQueueStatusProps {
  queueDepth: number;
  runningCount: number;
  maxConcurrent: number;
}

export function ExecutionQueueStatus({ queueDepth, runningCount, maxConcurrent }: ExecutionQueueStatusProps) {
  const utilization = maxConcurrent > 0 ? Math.round((runningCount / maxConcurrent) * 100) : 0;

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="mb-2 font-semibold">Execution Queue</h4>
      <div className="grid grid-cols-3 gap-3 text-center">
        <div>
          <p className="text-2xl font-bold text-blue-600">{runningCount}</p>
          <p className="text-xs text-gray-500">Running</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-yellow-600">{queueDepth}</p>
          <p className="text-xs text-gray-500">Queued</p>
        </div>
        <div>
          <p className="text-2xl font-bold">{utilization}%</p>
          <p className="text-xs text-gray-500">Utilization</p>
        </div>
      </div>
      <div className="mt-3 h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-2 rounded-full transition-all ${utilization >= 90 ? "bg-red-500" : utilization >= 60 ? "bg-yellow-500" : "bg-green-500"}`}
             style={{ width: `${utilization}%` }} />
      </div>
      <p className="mt-1 text-xs text-gray-400">{runningCount}/{maxConcurrent} slots used</p>
    </div>
  );
}
