"use client";
interface LatHistogramPanelProps { buckets: Record<string, number>; total: number; endpoint: string; }
export function LatHistogramPanel({ buckets, total, endpoint }: LatHistogramPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Latency Histogram</h3>
        <span className="text-xs text-gray-400">{endpoint} · {total} samples</span>
      </div>
      <div className="p-4 space-y-1">
        {Object.entries(buckets).map(([bucket, pct]) => (
          <div key={bucket} className="flex items-center gap-2 text-xs">
            <span className="w-14 text-gray-400 text-right">{bucket.replace("le_", "≤")}ms</span>
            <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded">
              <div className="h-full bg-blue-500 rounded" style={{ width: `${pct}%` }} />
            </div>
            <span className="w-10 text-right text-gray-400">{pct}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
