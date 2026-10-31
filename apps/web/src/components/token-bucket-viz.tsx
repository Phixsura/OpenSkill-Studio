"use client";

interface BucketInfo { key: string; tokens: number; capacity: number; pctFull: number; }
interface TokenBucketVizProps { buckets: BucketInfo[]; refillRate: number; }

export function TokenBucketViz({ buckets, refillRate }: TokenBucketVizProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🪣 Token Buckets</h3>
        <span className="text-xs text-gray-400">{refillRate}/s refill · {buckets.length} keys</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {buckets.map(b => (
          <div key={b.key} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-1">
              <span className="font-mono">{b.key}</span>
              <span className="text-gray-400">{b.tokens}/{b.capacity} ({b.pctFull}%)</span>
            </div>
            <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full transition-all ${b.pctFull < 20 ? "bg-red-500" : b.pctFull < 50 ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${b.pctFull}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
