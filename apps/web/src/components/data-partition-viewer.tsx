"use client";

interface DataPartitionViewerProps { numShards: number; distribution: Record<string, number>;
  maxDeviationPct: number; rebalanceNeeded: boolean; }

export function DataPartitionViewer({ numShards, distribution, maxDeviationPct, rebalanceNeeded }: DataPartitionViewerProps) {
  const total = Object.values(distribution).reduce((a, b) => a + b, 0);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🗂️ Data Partitions</h3>
        <span className={`text-xs ${rebalanceNeeded ? "text-yellow-600" : "text-green-600"}`}>
          {numShards} shards · {maxDeviationPct}% skew
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(distribution).map(([shard, count]) => {
          const pct = Math.round(count / Math.max(total, 1) * 100);
          return (
            <div key={shard} className="px-4 py-2">
              <div className="flex justify-between text-xs mb-1">
                <span className="font-mono">{shard}</span>
                <span className="text-gray-400">{count.toLocaleString()} ({pct}%)</span>
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
