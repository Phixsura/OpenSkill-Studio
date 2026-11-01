"use client";

interface BatchInfo { batch_id: string; total: number; succeeded: number; failed: number; }
interface Props { batches: BatchInfo[]; avgBatchSize: number; appName: string; }

export default function APIDeveloperAPIApiBatchRequestHandlerCard({ batches, avgBatchSize, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📦 Batch Requests</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — avg size: {avgBatchSize}</p>
        </div>
        <span className="text-[10px] text-gray-400">{batches.length} batches</span>
      </div>
      {batches.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No batch requests</p>
      ) : (
        <div className="space-y-1.5">
          {batches.map((b) => (
            <div key={b.batch_id} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{b.batch_id}</span>
              <div className="flex gap-2">
                <span className="text-green-600">{b.succeeded} ok</span>
                {b.failed > 0 && <span className="text-red-500">{b.failed} fail</span>}
                <span className="text-gray-400">/{b.total}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
