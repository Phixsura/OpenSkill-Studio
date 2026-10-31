"use client";

interface MetricBucket { timestamp: string; avg: number; min: number; max: number; count: number; }
interface MetricChartProps { buckets: MetricBucket[]; globalAvg: number; globalMin: number; globalMax: number; interval: string; }

export function MetricChart({ buckets, globalAvg, globalMin, globalMax, interval }: MetricChartProps) {
  const maxVal = Math.max(...buckets.map(b => b.max), 1);
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Metrics</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>avg: {globalAvg}</span>
          <span>min: {globalMin}</span>
          <span>max: {globalMax}</span>
        </div>
      </div>
      <div className="flex items-end gap-1 h-24">
        {buckets.map((b, i) => (
          <div key={i} className="flex-1 flex flex-col items-center gap-0.5" title={`${b.timestamp}: avg ${b.avg}`}>
            <div className="w-full rounded-t bg-blue-500 transition-all"
              style={{ height: `${(b.avg / maxVal) * 100}%`, minHeight: 4 }} />
          </div>
        ))}
      </div>
      <p className="text-center text-xs text-gray-400">{buckets.length} intervals ({interval})</p>
    </div>
  );
}
