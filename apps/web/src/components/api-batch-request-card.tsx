"use client";

interface BatchInfo {
  batch_id: string;
  total: number;
  success_count: number;
  failure_count: number;
  all_complete: boolean;
}

interface APIBatchRequestCardProps {
  batches: BatchInfo[];
  appName: string;
}

export default function APIBatchRequestCard({ batches, appName }: APIBatchRequestCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📦 Batch Requests</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{batches.length} batches</span>
      </div>

      {batches.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No batch requests</p>
      ) : (
        <div className="space-y-1.5">
          {batches.map((b) => (
            <div key={b.batch_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${b.all_complete ? (b.failure_count === 0 ? "bg-green-500" : "bg-yellow-500") : "bg-blue-500"}`} />
                <span className="text-xs text-gray-700 dark:text-gray-300">{b.batch_id}</span>
              </div>
              <span className="text-[10px] text-gray-400">{b.success_count}/{b.total} ok</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
