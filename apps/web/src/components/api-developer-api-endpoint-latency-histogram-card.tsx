"use client";

interface HistogramInfo { endpoint: string; avg_ms: number; p99_bucket: number; total: number; buckets: Record<number, number>; }
interface Props { histograms: HistogramInfo[]; appName: string; }

export default function APIDeveloperAPIEndpointLatencyHistogramCard({ histograms, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Latency Histogram</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {histograms.length} endpoints</p>
      </div>
      {histograms.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No latency data</p>
      ) : (
        <div className="space-y-3">
          {histograms.map((h) => (
            <div key={h.endpoint} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{h.endpoint}</span>
                <span className="text-gray-400">{h.total.toLocaleString()} reqs</span>
              </div>
              <div className="mt-1 flex gap-3 text-[10px]">
                <span className="text-blue-600">avg: {h.avg_ms}ms</span>
                <span className="text-orange-500">p99: {h.p99_bucket}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
