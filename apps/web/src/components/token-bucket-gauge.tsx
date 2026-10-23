"use client";

interface TokenBucketGaugeProps { tokens: number; capacity: number; refillRate: number; fillPct: number; }

export function TokenBucketGauge({ tokens, capacity, refillRate, fillPct }: TokenBucketGaugeProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🪣 Token Bucket</h3>
      <div className="text-center mb-3">
        <p className="text-3xl font-bold">{tokens}<span className="text-lg text-gray-300">/{capacity}</span></p>
        <p className="text-xs text-gray-400">tokens available</p>
      </div>
      <div className="h-6 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden mb-3 relative">
        <div className={`h-full rounded-full transition-all ${fillPct > 50 ? "bg-green-500" : fillPct > 20 ? "bg-yellow-500" : "bg-red-500"}`}
             style={{ width: `${fillPct}%` }} />
        <span className="absolute inset-0 flex items-center justify-center text-xs font-medium">{fillPct}%</span>
      </div>
      <p className="text-xs text-center text-gray-400">Refill: {refillRate} tokens/sec</p>
    </div>
  );
}
