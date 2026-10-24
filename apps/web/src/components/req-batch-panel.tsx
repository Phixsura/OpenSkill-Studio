"use client";
interface ReqBatchPanelProps { bufferSize: number; maxBatchSize: number; batchesFlushed: number; }
export function ReqBatchPanel({ bufferSize, maxBatchSize, batchesFlushed }: ReqBatchPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📦 Request Batcher</h3>
        <span className="text-xs text-gray-400">{batchesFlushed} batches flushed</span>
      </div>
      <div className="p-4">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-400">Buffer</span>
          <span>{bufferSize}/{maxBatchSize}</span>
        </div>
        <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full">
          <div className="h-full bg-blue-500 rounded-full transition-all"
            style={{ width: `${bufferSize / maxBatchSize * 100}%` }} />
        </div>
      </div>
    </div>
  );
}
