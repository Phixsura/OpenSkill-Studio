"use client";

interface BucketInfo {
  bucket_id: string;
  capacity: number;
  refill_rate: number;
  available: number;
}

interface TokenBucketCardProps {
  buckets: BucketInfo[];
  appName: string;
}

export default function TokenBucketCard({ buckets, appName }: TokenBucketCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🪣 Token Buckets
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{buckets.length} buckets</span>
      </div>

      {buckets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No token buckets</p>
      ) : (
        <div className="space-y-3">
          {buckets.map((b) => {
            const pct = b.capacity > 0 ? Math.round((b.available / b.capacity) * 100) : 0;
            const barColor =
              pct <= 10 ? "bg-red-500" : pct <= 30 ? "bg-yellow-500" : "bg-green-500";
            return (
              <div key={b.bucket_id}>
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-gray-700 dark:text-gray-300">
                    {b.bucket_id}
                  </span>
                  <span className="text-gray-400">
                    {b.available} / {b.capacity} tokens
                  </span>
                </div>
                <div className="mt-1 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                  <div className={`h-1.5 rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
                </div>
                <p className="mt-0.5 text-right text-[10px] text-gray-400">
                  {b.refill_rate}/s refill
                </p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
