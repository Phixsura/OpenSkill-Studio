"use client";

interface Bucket { label: string; count: number; }
interface Props { consumerId: string; totalRequests: number; p50: number; p95: number; p99: number; avg: number; buckets: Bucket[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiLatencyTrackerCard({ consumerId, totalRequests, p50, p95, p99, avg, buckets, appName }: Props) {
  const maxCount = Math.max(...buckets.map(b => b.count), 1);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏱️ Latency Distribution</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {totalRequests.toLocaleString()} requests</p>
      </div>
      <div className="mb-3 grid grid-cols-4 gap-2 text-center text-[11px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{avg}ms</div><div className="text-[9px] text-gray-400">Avg</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{p50}ms</div><div className="text-[9px] text-gray-400">P50</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-amber-600">{p95}ms</div><div className="text-[9px] text-gray-400">P95</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-red-600">{p99}ms</div><div className="text-[9px] text-gray-400">P99</div></div>
      </div>
      {buckets.length > 0 && (
        <div className="flex items-end gap-1" style={{ height: 40 }}>
          {buckets.map((b) => (
            <div key={b.label} className="flex flex-1 flex-col items-center gap-0.5">
              <div className="w-full rounded-t bg-blue-400" style={{ height: `${(b.count / maxCount) * 35}px` }} />
              <span className="text-[7px] text-gray-400">{b.label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
