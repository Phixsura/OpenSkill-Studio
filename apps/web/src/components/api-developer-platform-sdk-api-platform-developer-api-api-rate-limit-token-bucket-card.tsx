"use client";

interface BucketInfo { consumer_id: string; endpoint: string; capacity: number; available: number; refill_rate: number; }
interface Props { buckets: BucketInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiRateLimitTokenBucketCard({ buckets, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🪣 Token Buckets</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {buckets.length} buckets</p>
      </div>
      {buckets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No token buckets</p>
      ) : (
        <div className="space-y-1.5">
          {buckets.map((b) => (
            <div key={`${b.consumer_id}-${b.endpoint}`} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{b.consumer_id} → {b.endpoint}</span>
                <span className={b.available < b.capacity * 0.2 ? "text-red-600 dark:text-red-400" : "text-gray-400"}>{b.available}/{b.capacity}</span>
              </div>
              <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className="h-1 rounded-full bg-blue-500" style={{ width: `${(b.available / b.capacity) * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
