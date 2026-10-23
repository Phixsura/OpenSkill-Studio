"use client";

interface BatchProgressBarProps { totalItems: number; processed: number; failed: number;
  remaining: number; progressDisplay: string; batchesTotal: number; status: string; }

export function BatchProgressBar({ totalItems, processed, failed, remaining,
  progressDisplay, batchesTotal, status }: BatchProgressBarProps) {
  const pct = totalItems > 0 ? Math.round(((processed + failed) / totalItems) * 100) : 0;
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">📦 Batch Processing</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
          status === "completed" ? "bg-green-100 text-green-700" : "bg-blue-100 text-blue-700"
        }`}>{status}</span>
      </div>
      <div className="text-center mb-3">
        <p className="text-3xl font-bold">{progressDisplay}</p>
        <p className="text-xs text-gray-400">{processed.toLocaleString()} / {totalItems.toLocaleString()} items</p>
      </div>
      <div className="h-4 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden mb-3 flex">
        <div className="bg-green-500 h-full" style={{ width: `${(processed / Math.max(totalItems, 1)) * 100}%` }} />
        <div className="bg-red-400 h-full" style={{ width: `${(failed / Math.max(totalItems, 1)) * 100}%` }} />
      </div>
      <div className="flex justify-between text-xs text-gray-400">
        <span className="text-green-600">{processed.toLocaleString()} OK</span>
        {failed > 0 && <span className="text-red-500">{failed} failed</span>}
        <span>{remaining.toLocaleString()} remaining</span>
        <span>{batchesTotal} batches</span>
      </div>
    </div>
  );
}
