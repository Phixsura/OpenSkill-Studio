"use client";

interface BatchResult { batch: number; size: number; status: string; }
interface BatchProcPanelProps { totalItems: number; batchSize: number; totalBatches: number;
  failedBatches: number; elapsedMs: number; batches: BatchResult[]; }

export function BatchProcPanel({ totalItems, batchSize, totalBatches, failedBatches, elapsedMs, batches }: BatchProcPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📦 Batch Processor</h3>
        <span className={`text-xs ${failedBatches > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {totalBatches - failedBatches}/{totalBatches} OK · {elapsedMs}ms
        </span>
      </div>
      <div className="p-3 text-xs text-gray-400 text-center">
        {totalItems.toLocaleString()} items · batch size {batchSize}
      </div>
      <div className="border-t dark:border-gray-700 flex flex-wrap gap-1 p-3">
        {batches.map(b => (
          <div key={b.batch} className={`w-6 h-6 rounded flex items-center justify-center text-[10px] ${
            b.status === "success" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
            {b.batch}
          </div>
        ))}
      </div>
    </div>
  );
}
