"use client";

interface PercentileInfo { endpoint: string; p50: number; p90: number; p95: number; p99: number; count: number; }
interface Props { percentiles: PercentileInfo[]; appName: string; }

export default function APIDeveloperAPIApiResponseTimePercentilesCard({ percentiles, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📈 Response Percentiles</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {percentiles.length} endpoints</p>
      </div>
      {percentiles.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No data</p>
      ) : (
        <div className="space-y-2">
          {percentiles.map((p) => (
            <div key={p.endpoint} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{p.endpoint}</span>
                <span className="text-[10px] text-gray-400">{p.count.toLocaleString()} reqs</span>
              </div>
              <div className="mt-1 grid grid-cols-4 gap-1 text-center text-[10px]">
                <div><p className="font-bold text-green-600">{p.p50}ms</p><p className="text-[8px] text-gray-400">p50</p></div>
                <div><p className="font-bold text-blue-600">{p.p90}ms</p><p className="text-[8px] text-gray-400">p90</p></div>
                <div><p className="font-bold text-yellow-600">{p.p95}ms</p><p className="text-[8px] text-gray-400">p95</p></div>
                <div><p className="font-bold text-red-500">{p.p99}ms</p><p className="text-[8px] text-gray-400">p99</p></div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
