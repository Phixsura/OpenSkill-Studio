"use client";
interface LatencyTrackPanelProps { buckets: Record<string, number>; total: number; }
const BUCKET_COLOR: Record<string, string> = {
  "<10ms": "bg-green-500", "10-50ms": "bg-green-400", "50-100ms": "bg-yellow-400",
  "100-500ms": "bg-orange-400", ">500ms": "bg-red-500",
};
export function LatencyTrackPanel({ buckets, total }: LatencyTrackPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏱️ Latency Distribution</h3>
        <span className="text-xs text-gray-400">{total.toLocaleString()} samples</span>
      </div>
      <div className="p-4 space-y-1">
        {Object.entries(buckets).map(([bucket, count]) => (
          <div key={bucket} className="flex items-center gap-2 text-xs">
            <span className="w-16 text-gray-400">{bucket}</span>
            <div className="flex-1 h-3 bg-gray-200 dark:bg-gray-700 rounded">
              <div className={`h-full rounded ${BUCKET_COLOR[bucket] ?? "bg-gray-400"}`}
                style={{ width: `${count / Math.max(total, 1) * 100}%` }} />
            </div>
            <span className="w-8 text-right text-gray-400">{count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
