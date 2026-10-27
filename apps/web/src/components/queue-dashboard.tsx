"use client";

interface QueueStats { name: string; pending: number; processing: number; completed: number; dead: number; }

export function QueueDashboard({ queues }: { queues: QueueStats[] }) {
  if (!queues.length) return <div className="text-center text-gray-400 py-6 text-sm">No queues configured</div>;
  return (
    <div className="space-y-2">
      <h3 className="font-bold text-sm">Job Queues</h3>
      {queues.map(q => {
        const total = q.pending + q.processing + q.completed + q.dead;
        return (
          <div key={q.name} className="border dark:border-gray-700 rounded-xl p-3">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium text-sm">{q.name}</span>
              <span className="text-xs text-gray-500">{total} total</span>
            </div>
            <div className="flex gap-3 text-xs">
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-yellow-500" /> {q.pending} pending</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-blue-500" /> {q.processing} processing</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500" /> {q.completed} done</span>
              {q.dead > 0 && <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500" /> {q.dead} dead</span>}
            </div>
          </div>
        );
      })}
    </div>
  );
}
