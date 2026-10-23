"use client";

interface Bucket { bucket: number; count: number; avg: number; p95: number; min: number; max: number; }
interface RollupMetricsChartProps { buckets: Bucket[]; totalPoints: number; bucketMinutes: number; }

export function RollupMetricsChart({ buckets, totalPoints, bucketMinutes }: RollupMetricsChartProps) {
  const maxAvg = Math.max(...buckets.map(b => b.avg), 1);
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">📊 Metrics Rollup</h3>
        <span className="text-xs text-gray-400">{totalPoints.toLocaleString()} points · {bucketMinutes}min buckets</span>
      </div>
      <div className="flex items-end gap-0.5 h-24 mb-2">
        {buckets.map(b => (
          <div key={b.bucket} className="flex-1 flex flex-col items-center justify-end">
            <div className="w-full bg-blue-500 rounded-t" style={{ height: `${(b.avg / maxAvg) * 100}%` }}
                 title={`avg: ${b.avg}, p95: ${b.p95}`} />
          </div>
        ))}
      </div>
      <div className="grid grid-cols-4 gap-2 text-center text-xs text-gray-400">
        <span>Min: {buckets.length > 0 ? Math.min(...buckets.map(b => b.min)) : 0}</span>
        <span>Avg: {buckets.length > 0 ? (buckets.reduce((a, b2) => a + b2.avg, 0) / buckets.length).toFixed(1) : 0}</span>
        <span>P95: {buckets.length > 0 ? Math.max(...buckets.map(b => b.p95)) : 0}</span>
        <span>Max: {buckets.length > 0 ? Math.max(...buckets.map(b => b.max)) : 0}</span>
      </div>
    </div>
  );
}
