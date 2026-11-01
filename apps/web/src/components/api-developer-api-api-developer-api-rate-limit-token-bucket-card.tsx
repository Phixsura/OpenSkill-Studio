"use client";

interface BucketInfo { consumer_id: string; capacity: number; tokens: number; fill_pct: number; refill_rate: number; }
interface Props { buckets: BucketInfo[]; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiRateLimitTokenBucketCard({ buckets, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🪣 Token Buckets</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {buckets.length} buckets</p>
      </div>
      {buckets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No token buckets</p>
      ) : (
        <div className="space-y-2">
          {buckets.map((b, i) => (
            <div key={i}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{b.consumer_id}</span>
                <span className="text-gray-400">{Math.round(b.tokens)}/{b.capacity} · {b.refill_rate}/s</span>
              </div>
              <div className="mt-0.5 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1.5 rounded-full ${b.fill_pct < 20 ? "bg-red-500" : b.fill_pct < 50 ? "bg-yellow-500" : "bg-green-500"}`} style={{ width: `${b.fill_pct}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
