"use client";

interface BucketInfo { bucket_key: string; request_count: number; error_rate: number; avg_latency: number; }
interface Props { buckets: BucketInfo[]; totalRequests: number; peakBucket: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestLogAggregatorCard({ buckets, totalRequests, peakBucket, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Log Aggregator</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalRequests.toLocaleString()} total</p>
        </div>
        <span className="text-[10px] text-gray-400">peak: {peakBucket}</span>
      </div>
      {buckets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No aggregated data</p>
      ) : (
        <div className="space-y-1">
          {buckets.slice(-6).map((b) => (
            <div key={b.bucket_key} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{b.bucket_key}</span>
              <span className="text-gray-400">{b.request_count} · {b.avg_latency}ms · {b.error_rate}%err</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
